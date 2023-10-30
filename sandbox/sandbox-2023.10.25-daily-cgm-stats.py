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
df_entries = col_entries.find_pandas_all({}, schema=entries_schema)
df_treatments = col_treatments.find_pandas_all({}, schema=treatments_schema)
df_devicestatus = col_devicestatus.find_pandas_all({}, schema=devicestatus_schema)

# Convert the time string to datetime format (not converting time zone this time!)
df_entries["time"] = pd.to_datetime(df_entries["dateString"])


# #######################################################################################################

df_cgm_daily = oop.daily_cgm_stats(df_entries["time"], df_entries["sgv"])

sp.daily_tir(df_entries["time"], df_entries["sgv"])


