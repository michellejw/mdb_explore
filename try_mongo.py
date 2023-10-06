"""try_mongo.py
This is an initial exploration of the using pymongo to access CGM and Loop (insulin pump) data
"""
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import yaml

import mdb_tools

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

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Load the database
db = client[db_name]

# assign the "entries" collection
tab_entries = db["entries"]

# Example of querying the database
ent_list = []
for te in tab_entries.find({'direction': 'Flat'}):
    ent_list.append(te)

# Another (more useful) example of querying the database
ent_list= []
start_date = datetime(2023, 7, 5, 0, 0, 0)
date_query = {'dateString': {'$gt': start_date.isoformat() + '.000Z'}}
for te in tab_entries.find(date_query):
    ent_list.append(te)

