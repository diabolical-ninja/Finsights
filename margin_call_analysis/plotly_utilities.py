"""
Title:  Plotly Utilities
Desc:   Helper functions for generating plotly graphics
Author: Yassin Elathir
Date:   2017-12-30
"""

import pandas as pd
import plotly.graph_objs as go


# Basic Candlesticks
def candles(df, open, high, low, close, time, title, base_currency):
    """
    Generates Candlesticks


    :param df:
    :param open:
    :param high:
    :param low:
    :param close:
    :param time:

    :return:
    """

    data = [go.Candlestick(x=df[time],
                           open=df[open],
                           high=df[high],
                           low=df[low],
                           close=df[close]
                           )]

    layout = go.Layout(
        title=title,
        yaxis=dict(title=base_currency),
        xaxis=dict(title='Timestamp')
    )

    fig = go.Figure(data=data, layout=layout)

    return fig


def timeseries(df, x, y, title='', xlabel='', ylabel='', lines=None, shape='wide', key_col='', keys=''):
    """Simple Timeseries Plot
    
    Args:
        df (data.frame): DataFrame to use for plotting
        x (str): Name of Time/Date/etc column for x-axis
        y (str or list): Value column to plotList of columns
        title (str, optional): Defaults to ''. Plot Title
        xlabel (str, optional): Defaults to ''. xaxis label. Defaults to Timestamp
        ylabel (str, optional): Defaults to ''. yaxis label
        lines (dict, optional): Defaults to None. Vertical/Horizontal line information to overlay on timeseries
        shape (str, optional): Defaults to 'wide'.
            - Must be either "wide" or "long"
            - Wide: Variable/s occupy unique columns
            - Long: Key+Value pair setup
        key_col (str, optional): Defaults to ''.
            - Only required if shape = "long"
            - The column name containing the lookup keys
        keys (str, optional): Defaults to ''.
            - The keys to charts
    
    Returns:
        Plotly scatter plot figure
    """

    # Charting requires list input but string accepted to make the users life a tad easier
    if not isinstance(y, list):
        y = [y]
    if not isinstance(keys, list):
        keys = [keys]

    if lines is None:
        lines = []

    # Generate data for chart based on structure of the data
    if shape=='wide':
        data = [go.Scatter(
            x=df[x],
            y=df[vals],
            name=vals
        ) for vals in y]

    elif shape=='long':
        if key_col == '':
            raise ValueError("Please provide the column name containing your series names")
        
        data = [go.Scatter(
            x = df[df[key_col]==key][x],
            y = df[df[key_col]==key][y[0]],
            name = key
        ) for key in keys]
    else:
        raise ValueError("Please provide a valid shape")

    layout = go.Layout(
        title=title,
        xaxis=dict(title=xlabel),
        yaxis=dict(title=ylabel),
        shapes=lines
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


def create_line(action, timestamp, y_min, y_max):
    """
    A not very generic function that generates vertical lines to be overlaid on a time series chart

    :param action:    Whether to buy or sell
    :param timestamp: The timestamp to perform the action
    :param y_min:     Minimum value to start the vertical line from
    :param y_max:     Maximum value to end the vertical line at

    :return: Dictionary containing the line details that can be added to a shape object in Plotly
    """

    if action == 1:
        colour = 'blue'
    elif action == -1:
        colour = 'red'

    return {
        'type': 'line',
        'x0': timestamp,
        'y0': y_min,
        'x1': timestamp,
        'y1': y_max,
        'line': {
            'color': colour,
            'width': 2,
            'dash': 'dot'
        }
    }




def histogram(df, values, title='', xlabel='', ylabel='', shape='wide', key_col='', keys=''):
    """Plotly Historgram Helper Function
    
    Args:
        df (data.frame): Your data
        values (str or list): The column/s to plot
        keys (str)
        title (str, optional): Defaults to ''. Plot title
        xlabel (str, optional): Defaults to ''. X-axis title
        ylabel (str, optional): Defaults to ''. Y-axis title
        shape (str, optional): Defaults to 'wide'.
            - Must be either "wide" or "long"
            - Wide: Variable/s occupy unique columns
            - Long: Key+Value pair setup
        key_col (str, optional): Defaults to ''.
            - Only required if shape = "long"
            - The column name containing the lookup keys
        keys (str, optional): Defaults to ''.
            - The keys to charts

    Returns:
        Plotly histogram figure
    """

    # Charting requires list input but string accepted to make the users life a tad easier
    if not isinstance(values, list):
        values = [values]
    if not isinstance(keys, list):
        keys = [keys]

    # Generate data for chart based on structure of the data
    if shape=='wide':
        data = [go.Histogram(
            x = df[vals],
            name = vals
        ) for vals in values]

    elif shape=='long':
        if key_col == '':
            raise ValueError("Please provide the column name containing your series names")
        
        data = [go.Histogram(
            x = df[df[key_col]==key][values[0]],
            name = key
        ) for key in keys]

    else:
        raise ValueError("Please provide a valid shape")

    # Generate niceties
    layout = go.Layout(
            title= title,
            yaxis=dict(title=ylabel),
            xaxis=dict(title=xlabel)
            )

    fig = go.Figure(data=data, layout=layout)
    return fig