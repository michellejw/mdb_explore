"""loop_stats.py

A module for extracting and computing statistics for insulin or CGM data
"""


# import numpy as np
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
