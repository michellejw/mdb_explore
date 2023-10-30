"""loop_stats.py

A module for extracting and computing statistics for insulin or CGM data
"""
import numpy as np
import pandas as pd


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


def get_setting_at_times(in_times, col_prof, req_setting="carbratio", req_profile="Default"):
    """
    A function that returns the requested profile setting from a profile collection at requested times

    Args:
        in_time (array-like): An array of input / requested times in pandas datetime format
        col_prof (mongodb collection): profile collection that includes the carb ratios
        req_setting (str): requested profile setting. Can be "carbratio", "sens", or "basal"
        req_profile (str): requested profile name. Default is "Default".

    Returns: (list) requested setting at the requested date/times

    """
    # ##### Prep time variables #####

    # Convert in_times array to series (if it isn't already)
    in_times = pd.Series(in_times)

    # Convert requested input times to unix
    in_times_unix = in_times.view('int64')

    # Compute seconds elapsed in current day (to get at the current carb ratio)
    seconds_in_day = in_times.dt.hour * 3600 + in_times.dt.minute * 60 + in_times.dt.second

    # ##### Prep profile documents #####

    # Dump every profile document into a list
    prof_docs_all = [prof for prof in col_prof.find({})]

    # Get all the time stamps and convert to unix time (nanoseconds)
    prof_time_unix = [int(prof["mills"]) * 1e6 for prof in prof_docs_all]

    # Get all the "store" items in each document
    all_store = [doc["store"] for doc in prof_docs_all]

    # Pull out all the keys for each "store"
    store_keys = [x.keys() for x in all_store]

    # Extract the "store" info for each document, for any available profiles
    all_store_vals = [[doc[key] for key in store_keys[doc_num]] for doc_num, doc in enumerate(all_store)]

    # Extract the profile names for each document
    all_store_profiles = [[key for key in store_keys[doc_num]] for doc_num, doc in enumerate(all_store)]

    # ##### Next, figure out which profile is appropriate for each requested time #####

    # Get the indices of the most "recent" documents from the collection. Only keep the ones for the requested profile.
    doc_idx = [(len([in_time - t for t_idx, t in enumerate(prof_time_unix) if
                     (in_time - t >= 0) & (req_profile in all_store_profiles[t_idx])]) - 1) for in_time in
               in_times_unix]

    # Profile info for each requested time
    requested_prof_info = [[all_store[this_doc][prof] for prof in all_store_profiles[this_doc]] for this_doc in doc_idx]

    val_req = []
    for idx, prof_info in enumerate(requested_prof_info):
        if req_setting in prof_info[0].keys():
            carb_ratio = prof_info[0][req_setting]
        else:
            raise Exception(
                "The requested setting, " + req_setting + ", is not one of: " + ', '.join(list(prof_info[0].keys())))

        # Ensure that the input time zone (CGM) matches the profile/treatment time zone
        this_req_time_in = in_times.iloc[idx].tz_convert(prof_info[0]['timezone'])
        this_req_time = this_req_time_in.hour * 3600 + this_req_time_in.minute * 60 + this_req_time_in.second

        # Convert treatment time to seconds in day using hours and minutes
        times = [int(cr["time"].split(':')[0]) * 3600 + int(cr["time"].split(':')[1]) * 60 for cr in carb_ratio]
        crs = [cr["value"] for cr in carb_ratio]

        t_diff = [this_req_time - t for t in times]

        val_req.append([crs[idx] for idx, x in enumerate(t_diff) if x > 0][-1])

    return val_req


def get_last_doc(col):
    """
    Get the last/most recent document in the collection
    """
    return [prof for prof in col.find().skip(col.estimated_document_count() - 1)][0]


def daily_cgm_stats(time_vec, cgm_data, min_target=70, max_target=180):
    """
    Compute some general statistics per day including percent above, percent below, and percent in range.

    Args:
        time_vec (array-like): array or list or series of times
        cgm_data (array-like): array or list or series of CGM values at each point in time_vec. Must be same length as time_vec
        min_target (num, Optional): minimum blood glucose target in mg/dL, default is 70
        max_target (num, Optional): maximum blood glucose target in mg/dL, default is 180

    Returns: pandas dataframe containing daily statistics

    """
    yeardays = get_yeardays(time_vec)
    df_cgm_data = pd.DataFrame(np.transpose([time_vec, yeardays, cgm_data]), columns=["time", "yearday", "bg"])

    # COMPUTE STATS PER DAY
    df_cgm_daily = df_cgm_data[["bg", "yearday"]].groupby("yearday").describe()["bg"]
    df_cgm_daily["yearday"] = df_cgm_daily.index
    df_cgm_daily["time"] = pd.to_datetime(df_cgm_daily['yearday'], format='%Y-%j')

    unique_days = df_cgm_daily["yearday"].tolist()

    # Initialize lists
    pct_above = []
    pct_below = []
    pct_inrange = []

    # loop through each day (I'm sure there's a fancy way to do this with Pandas but I
    # can't figure it out...)
    for day in unique_days:
        df_sub = df_cgm_data[df_cgm_data["yearday"] == day]
        this_total = len(df_sub)
        if this_total > 0:
            pct_above.append(sum(df_sub["bg"] > max_target) / this_total * 100)
            pct_below.append(sum(df_sub["bg"] <= min_target) / this_total * 100)
            pct_inrange.append(sum((df_sub["bg"] > min_target) & (df_sub["bg"] <= max_target)) / this_total * 100)
        else:
            pct_above.append(0)
            pct_below.append(0)
            pct_inrange.append(0)

    df_cgm_daily["pct_above"] = pct_above
    df_cgm_daily["pct_below"] = pct_below
    df_cgm_daily["pct_inrange"] = pct_inrange

    return df_cgm_daily.drop(['count', 'unique', 'top', 'freq'], axis='columns')
