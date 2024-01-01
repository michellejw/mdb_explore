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


date_start = '2023-11-16'
dates = pd.date_range(date_start, periods=43, freq="D")
times = pd.date_range(date_start, periods=24, freq="H")
df_treatment_stats = pd.DataFrame(index=times)

test = oop.get_setting_at_times(times, col_treatments, req_setting="basal")
