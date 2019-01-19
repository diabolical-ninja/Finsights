"""
Title: Yahoo Finance Scraper
Description: Downloads EOD data from Yahoo Finance
"""

import requests
import re
from datetime import datetime
from time import mktime
from io import StringIO
import pandas as pd


def time_str_to_unix(date):
    """Converts a date string to a unix timestamp
    
    Args:
        date (str): Date of format YYYY-MM-DD
    
    Returns:
        int: unix timestamp
    """

    datum = datetime.strptime(date, '%Y-%m-%d')
    return int(mktime(datum.timetuple()))


def get_yahoo_history(symbol, start_date, end_date, frequency):
    """Scrapes data from the yahoo finance download data endpoint
    
    Args:
        symbol (str): Ticker symbol+including exchange. Eg "AFI.AX"
        start_date (str): Date in format of YYYY-MM-DD
        end_date (str): Date in format of YYYY-MM-DD
        frequency (str): Aggregate level. Options are:
            - daily
            - weekly
            - monthly
    
    Returns:
        pandas.core.frame.DataFrame: EOD data
    """

    # Get session info
    session_url = 'https://au.finance.yahoo.com/quote/{}/history'.format(symbol)
    session = requests.Session()
    yahoo_session = session.get(session_url)

    # Crumb required for each request
    yahoo_crumb = re.findall('"CrumbStore":{"crumb":"(.+?)"}', yahoo_session.text)[0]

    # Map frequency to what Yahoo expect
    if frequency == 'daily':
        frequency = '1d'
    elif frequency == 'weekly':
        frequency = '1wk'
    elif frequency == 'monthly':
        frequency = '1mo'
    else:
        raise ValueError("Please provide a valid frequncy. The options are daily, weekly or monthly")

    # "Download" data from Yahoo
    final_url = "https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval={}&events=history&crumb={}".format(
            symbol
            , time_str_to_unix(start_date)
            , time_str_to_unix(end_date)
            , frequency
            , yahoo_crumb
        )

    response = session.get(final_url)

    if response.status_code == 404:
        returned_error = response_json['chart']['error']['description']
        raise ValueError("From Yahoo: {}".format(returned_error))

    elif response.status_code == 200:

        # Extract data into DF
        response_data = StringIO(response.text)
        df = pd.read_csv(response_data)

        df['Date'] = pd.to_datetime(df['Date'])
        
        return df
    