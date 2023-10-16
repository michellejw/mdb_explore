"""try_mongo.py
This is an initial exploration of the using pymongo to access CGM and Loop (insulin pump) data
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

"""
Path to the yml secrets file which includes the mongo database URI.
This file is not located in the same folder because the URI contains sensitive information 
(e.g., password and database name)

The yml file is a simple text file and only requires the following:

secrets:
  mongo_uri: <mongo-uri-here>
  mongo_db: <db-name>

"""

# Path to the yml secrets file
yml_secrets_file = '../../secrets/mdb_secrets.yml'

# Load the yml file and read the URI and database name
with open(yml_secrets_file) as file:
    try:
        mdb_secrets = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        print(exc)
uri = mdb_secrets['secrets']['mongo_uri']
db_name = mdb_secrets['secrets']['mongo_db']

# Add extra find_* methods to pymongo collection objects (pymongoarrow):
pymongoarrow.monkey.patch_all()

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Load the database
db = client[db_name]

# load the "entries" collection
col_entries = db["entries"]

# load the "treatments" collection - this is the one that includes loop recordings of boluses, basal, etc
col_treatments = db["treatments"]

# Example of querying the database
ent_list = []
for te in col_entries.find({'direction': 'Flat'}):
    ent_list.append(te)

# Another (more useful) example of querying the database
ent_list= []
start_date = datetime(2023, 10, 4, 0, 0, 0)
date_query = {'dateString': {'$gt': start_date.isoformat() + '.000Z'}}
for te in col_entries.find(date_query):
    ent_list.append(te)

# Trying out the pymongoarrow method. Oh yes, this is WAY better.
df_entries = col_entries.find_pandas_all(
    {},
    schema=Schema({
        'sgv': float,
        'dateString': str,
    })
)

# load treatments collection into a dataframe
df_treatments = col_treatments.find_pandas_all(
    {},
    schema=Schema({
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
)

# Try it another way
entries_schema = Schema({
        'sgv': float,
        'dateString': str,
    })
start_date = datetime(2023, 9, 4, 0, 0, 0)
# this_query = {'dateString': {'$gt': start_date.isoformat() + '.000Z'}}
this_query = {'sgv': 183.0}

df = col_entries.find_pandas_all(this_query, schema=entries_schema)

# another try - this time doing the query on the collection then converting to pandas
start_date = datetime(2023, 7, 4, 0, 0, 0)
date_query = {'dateString': {'$gt': start_date.isoformat() + '.000Z'}}
cur_sub = col_entries.find(date_query)
col_sub = col_entries.find(date_query).collection
df = col_entries.find_pandas_all({}, schema=entries_schema)

