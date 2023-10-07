"""try_import_data.py
Import CGM and Loop (insulin pump) data from mongo atlas.
"""
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import yaml
import mdb_tools
# Pyarrow - importing mongo databases into pandas
import pyarrow
import bson
import pymongoarrow.monkey
from pymongoarrow.api import Schema, find_pandas_all
# Add extra find_* methods to pymongo collection objects (pymongoarrow):
pymongoarrow.monkey.patch_all()

# Path to the yml secrets file
yml_secrets_file = '../secrets/mdb_secrets.yml'

# Load the yml file and read the URI and database name
with open(yml_secrets_file) as file:
    try:
        mdb_secrets = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        print(exc)
uri = mdb_secrets['secrets']['mongo_uri']
db_name = mdb_secrets['secrets']['mongo_db']

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Load the database
db = client[db_name]

# load the "entries" collection
col_entries = db["entries"]

# load the "treatments" collection - this is the one that includes loop recordings of boluses, basal, etc
col_treatments = db["treatments"]

# Make the schemas
entries_schema = Schema({
    'sgv': float,
    'dateString': str,
})

treatment_schema = Schema({
    'duration': float,
    'amount': float,
    'absolute': float,
    'timestamp': str,
    'created_at': str,
    'rate': float,
    'temp': str,
    'automatic': bool,
    'eventType': str,
})

df_entries = col_entries.find_pandas_all({}, schema=entries_schema)
df_treatment = col_treatments.find_pandas_all({}, schema=treatment_schema)


