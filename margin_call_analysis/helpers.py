"""
Title: Margin Loan LVR Analysis Helper Functions
Desc:  A collection of helper functions used throughout the analysis
"""

import numpy as np
import pandas as pd
from string import digits
import math
from alpha_vantage.timeseries import TimeSeries


def remove_numbers(string: str) -> str:
    """Strips numbers from a string

    Eg, a1b2c3 -> abc
    
    Args:
        string (str): String to clean
    
    Returns:
        str: Provided string without numbers
    """
    
    from string import digits
    return string.translate(str.maketrans('', '', digits))



def get_historical_data(key, time_slice, symbol):
    """Wrapper function to source historical EOD stock data
    
    Args:
        key (str): alphavantage api key
        time_slice (str): Aggregate level to fetch. Options are:
                - daily
                - weekly
                - monthly
        symbol (str): Symbol used, including the exchange
    
    Returns:
        DataFrame: EOD dataframe
    """


    # Instantiate Session
    ts = TimeSeries(key=key, output_format='pandas', indexing_type='integer')
    
    # Retrieve Data
    if(time_slice=='daily'):
        df, metadata = ts.get_daily(symbol, outputsize='full')
    elif(time_slice=='weekly'):
        df, metadata = ts.get_weekly(symbol)
    elif(time_slice=='monthly'):
        df, metadata = ts.get_monthly(symbol)

    # Replace 0's with NA's because they're almost certainly false
    df.replace(0, np.nan, inplace=True)

    # Fix crappy column header that contain numbers & periods
    df.columns = [remove_numbers(x).replace('. ','') for x in df.columns.tolist()]
    
    # Fix Date type
    df['date'] = pd.to_datetime(df['date'])
    
    return df


def calc_lvr(df, initial_investment, initial_lvr):
    """For a given investment, calculates LVR at each time unit based on price fluctuations
    
    Uses close price for the calcs

    Args:
        df (data.frame): EOD dataframe
        initial_investment (int): Sum of personal contribution + loan
        initial_lvr (float): Decimal percentage of loan value ratio (lvr)
    
    Returns:
        data.frame: Timeseries data frame with price, investment value & LVR
    """

    # Determine Amount borrowed
    borrowed_investment = initial_investment/(1-initial_lvr) * initial_lvr
    total_investment = initial_investment + borrowed_investment
    
    # Initial number of shares
    # start_price = df[df['date']==df['date'].min()]['close'][0]
    start_price = df[df.close > 0]['close'].iloc[0]
    initial_holdings = math.floor(total_investment/start_price)
    
    # Historical LVR's
    df_lvr = pd.DataFrame({
        'date': df.date,
        'price': df.close,
        'value': df.close * initial_holdings,
        'lvr': borrowed_investment/(df.close * initial_holdings)
    })
    
    return df_lvr


def calc_drawdown(df, price_col, window_size):
    """Calculates drawdown

    Reference: https://www.investopedia.com/terms/d/drawdown.asp
    
    Args:
        df (data.frame): Price history dataframe
        price_col (str): Column name for price data
        window_size (int): How many units to look back. Units change based on aggregate provided
    
    Returns:
        data.frame: Original dataframe with drawdown appended
    """


    # Calculate rolling prior maximum to compare against current price
    prior_max = df[price_col].rolling(window=window_size, min_periods=1).max()

    # Calculate percentage change, aka drawdown
    df['market_drawdown'] = (df[price_col]/prior_max - 1.0) * 100
    df['market_drawdown'].replace(-100, 0, inplace=True)
    
    return df


def calc_margin_call_drop(current_lvr, base_lvr, buffer = 0.0):
    """Calculates the % drop required to trigger a margin call
    
    Args:
        current_lvr (float): LVR on the loan
        base_lvr (float): Max LVR allowed
        buffer (float, optional): Defaults to 0.0. LVR buffer that triggers a drawdown

    Returns:
        float: Decimal representation of % drop required to trigger a margin call
    """

    return (1 - current_lvr/(base_lvr+buffer))*100


def calc_max_safe_lvr(max_drawdown, base_lvr, buffer = 0.0):
    """Calculates maximum safe LVR to have historically avoided a margin call
    
    Args:
        max_drawdown (float): Maximum historically observed drawdown
        base_lvr (float): Max LVR allowed
        buffer (float, optional): Defaults to 0.0. LVR buffer that triggers a drawdown

    Returns:
        float: Decimal representation of max historically safe LVR
    """
    
    max_drawdown = max_drawdown if max_drawdown < 0 else -1*max_drawdown
        
    return (100 + max_drawdown) * (base_lvr + buffer)


def create_margin_call_range_table(max_lvr, buffer=0.1, step_size=0.01):
    """Creates a lookup table of % drop required to trigger a margin call for the various cLVR's provided
    
    Args:
        max_lvr (float): Decimal for upper bound on allowed LVR
        buffer (float, optional): Defaults to 0.1. LVR buffer prior to margin call
        step_size (float, optional): Defaults to 0.01. How granular to make the intervals

    Returns:
        data.frame: Table containing % drop required to trigger a margin call at each LVR
    """

    lvr_range = np.arange(0, max_lvr+buffer+step_size, step_size)
    df = pd.DataFrame({
        "lvr": lvr_range,
        "mc_trigger": [calc_margin_call_drop(x, max_lvr, buffer) for x in lvr_range]
    })

    return df


def margin_call_samples(key, symbol, time_slice, drawdown_window, lvr_lookup):
    """Helper function to wrap all steps
    
    Args:
        symbol (str): Ticker code, noting to append exchange if required
        time_slice (str): daily, weekly or monthly
        drawdown_window (int): Number of periods to lookup. Note the units change based on the timeslice above
        lvr_lookup (data.frame): Lookup table with LVRs & their corresponding margin call trigger
    
    Returns:
        data.frame: Historical EOD data
        data.frame: Lookup table with margin call frequency appended
        float: Max safe LVR that would have historically avoided a margin call
    """

    # Get historical price data
    df_eod = get_historical_data(key = key, time_slice=time_slice, symbol=symbol)
    df_eod['symbol'] = symbol
    
    # Calculate Drawdown
    df_eod = calc_drawdown(df_eod, price_col = 'close', window_size = drawdown_window)
    
    # Count margin calls for each LVR
    mc_counts = list()
    for row, col in lvr_lookup.iterrows():
        # Identify drawdowns that would have caused a margin call
        margin_calls = df_eod['market_drawdown'].apply(
            lambda x: 1 if abs(x) > col['mc_trigger'] and x < 1 else 0)

        # Count instances
        counts = margin_calls.value_counts()
        mc_count = counts[1] if(len(counts)>1) else 0
        mc_counts.append(mc_count)

    lvr_lookup["{}_mc_count".format(symbol.replace(".","_"))] = mc_counts
    
    # Calculate historically safe max LVR (note buffer absorbed into max lvr)
    max_historical_safe_lvr = calc_max_safe_lvr(df_eod.market_drawdown.min(), lvr_lookup.lvr.max())
    
    return df_eod, lvr_lookup, max_historical_safe_lvr