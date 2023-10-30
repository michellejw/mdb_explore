"""Module for plotting BG and insulin data

This module contains functions for plotting both blood glucose and insulin data.

"""
import sys

sys.path.append("../")

import matplotlib.pyplot as plt
import seaborn as sns

from mdb_tools import loop_stats as oop


def daily_tir(time_vec, cgm_data, min_target=70, max_target=180):
    """
    Daily time in range, presented as a bar plot.
    Plot a bar chart of daily time in range from CGM data

    Example usage:
    fig, ax = daily_bars(df_cgm_daily)

    Args
        time_vec (array-like): array or list or series of times
        cgm_data (array-like): array or list or series of CGM values at each point in time_vec. Must be same length as time_vec
        min_target (num, Optional): minimum blood glucose target in mg/dL, default is 70
        max_target (num, Optional): maximum blood glucose target in mg/dL, default is 180

    Returns:
        A 2-element tuple

        - **fig** (matplotlib figure object)
        - **ax** (matplotlib axis object)
    """

    # Load daily CGM stats
    df_cgm_daily = oop.daily_cgm_stats(time_vec, cgm_data)

    # Generate bar plot
    fig, ax = plt.subplots(1, 1, figsize=(8, 4))

    ax.bar(df_cgm_daily["time"], df_cgm_daily["pct_below"],
           color="tomato", alpha=1, label="% below")

    ax.bar(df_cgm_daily["time"], df_cgm_daily["pct_inrange"],
           bottom=df_cgm_daily["pct_below"],
           color="cornflowerblue", alpha=1, label="% in range")

    ax.bar(df_cgm_daily["time"], df_cgm_daily["pct_above"],
           bottom=df_cgm_daily["pct_below"] + df_cgm_daily["pct_inrange"],
           color="lightsteelblue", alpha=0.7, label="% above")

    ax.spines[['right', 'top']].set_visible(False)

    ax.legend(ncol=1)
    sns.despine(left=False, bottom=True, ax=ax)

    ax.set_title("Target range: " + str(min_target) + " - " + str(max_target) + " mg/dL")

    return fig, ax
