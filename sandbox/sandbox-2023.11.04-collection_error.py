"""
Extract basic, daily CGM stats
"""

import sys
sys.path.append("../")

from mdb_tools import load_data as ld
from mdb_tools import schemas
from mdb_tools import loop_stats as oop
from mdb_tools import sugar_plots as sp

import pandas as pd

yml_secrets_file = '../../secrets/mdb_secrets.yml'

# Access the database using the yml secrets file, and get a specific set of "collections"
col_entries, col_treatments, col_profile, col_devicestatus = ld.get_collections(yml_secrets_file)

# Grab schemas
entries_schema, treatments_schema, devicestatus_schema = schemas.mdb_schemas()

# Load
df_entries0 = col_entries.find_pandas_all({}, schema=entries_schema)
df_treatments = col_treatments.find_pandas_all({}, schema=treatments_schema)
df_devicestatus = col_devicestatus.find_pandas_all({}, schema=devicestatus_schema)

# Remove duplicate entries from cgm date - keep only loop for now.
df_entries = df_entries0[df_entries0["device"]=="loop://Dexcom/G6/21.0"].copy()

# Convert the time string to datetime format
time_zone = 'US/Eastern'
df_entries["time"] = pd.to_datetime(df_entries["dateString"]).dt.tz_convert(time_zone)
df_entries.set_index("time", inplace = True)
df_entries.sort_index(inplace=True)

# Set up my start/end dates and start/end times
date_start = '2023-11-03'
date_end = '2023-11-04'

# start and end time in hours/time of day
time_start = 0
time_end = 24

# Extract only the dates of interest
in_times = df_entries.loc[date_start:date_end].index.to_series()

#in_times = df_entries["time"]

# Pulling settings at each CGM time - making sure it's working!
test = oop.get_setting_at_times(in_times, col_devicestatus, req_setting = "pump", req_profile = "Default")
# #######################################################################################################
#
# df_cgm_daily = oop.daily_cgm_stats(df_entries["time"], df_entries["sgv"])
#
# sp.daily_tir(df_entries["time"], df_entries["sgv"])


