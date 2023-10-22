"""stats.py

A module for extracting and computing statistics for insulin or CGM data
"""


# import numpy as np


def get_yeardays(time_series):
    """
    Read pandas datetime series and return a string of "year-day"

    Args:
    time_series (series): Pandas series constructed from glooko data. Time column must be in Pandas datetime format.

    Returns:
    pandas series: year-day

    """
    day_of_year = time_series.dt.dayofyear
    year = time_series.dt.year

    return year.astype(str) + '-' + day_of_year.map('{:03.0f}'.format)
