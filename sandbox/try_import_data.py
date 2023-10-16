"""try_import_data.py
Import CGM and Loop (insulin pump) data from mongo atlas.
"""
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import yaml

# Pyarrow - importing mongo databases into pandas
import pymongoarrow.monkey
from mdb_tools.schemas import mdb_schemas
import pyarrow as pa
from pymongoarrow.api import Schema

# Add extra find_* methods to pymongo collection objects (pymongoarrow):
pymongoarrow.monkey.patch_all()

# Path to the yml secrets file
yml_secrets_file = '../../../secrets/mdb_secrets.yml'

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

# Load "profile" collection
col_profile = db["profile"]

# Load "devicestatus" collection
col_devicestatus = db["devicestatus"]

treatment_schema, entries_schema, devicestatus_schema, profile_schema = mdb_schemas()

df_entries = col_entries.find_pandas_all({}, schema=entries_schema)
df_treatment = col_treatments.find_pandas_all({}, schema=treatment_schema)
df_devicestatus = col_devicestatus.find_pandas_all({}, schema=devicestatus_schema)





profile_project = {'$project': {
    'carbRatios': '$store.Default.carbratio',
    'isp': '$store.Default.sens',
    'carbs_hr': '$store.Default.carbs_hr',
    'startDate': '$startDate'
}}

profile_schema = Schema({
    'carbs_hr': float,
    'startDate': str
})

col_profile.aggregate_pandas_all([
    {'match': {}},
    profile_project],
    schema=profile_schema)

col_profile.aggregate_pandas_all([{'match':{}},],
                                 schema=profile_schema)


list(col_profile.aggregate([
    {'$match': {}},
    {'$project': {
        'carbRatios': '$store.Default.carbratio',
        'isp': '$store.Default.sens',
        'carbs_hr': '$store.Default.carbs_hr',
        'startDate': '$startDate'
    }}
]))

# col_profile.aggregate([
#     # {'$match': {'units': 'mg/dl'}},
#     {'$project': {
#         'carbRatios': '$store.Alma.carbratio',
#         'isp': '$store.Alma.sens',
#         'carbs_hr': '$store.Alma.carbs_hr',
#         'created_at': '$created_at'
#     }}
# ])

fields = [
    ('time', pa.string()),
    ('value', pa.int64()),
]
dftest = col_profile.aggregate_pandas_all([
    {'$match': {}},
    {'$project': {
        'ogCarbRatios': '$store.Alma.carbratio',
        'carbRatios': '$store.Default.carbratio',
        'isp': '$store.Default.sens',
        'ogCarbs_hr': '$store.Alma.carbs_hr',
        'carbs_hr': '$store.Default.carbs_hr',
        'startDate': '$startDate',
        'Default': '$defaultProfile'
    }}
],
    schema=Schema({
        'ogCarbs_hr': float,
        'carbs_hr': str,
        'startDate': str,
        'Default': str,
        'carbRatios': pa.struct({'time': pa.string(),
                                 'value': pa.int32(),
                                 'timeAsSeconds': pa.int32()})
    })
)

fields = [
    pa.field('f1', pa.int32()),
    pa.field('f2', pa.string(), nullable=False),
]
Schema({"start": str, "prop": struct([field("start", int32())])})
COLUMN1_SCHEMA = pa.struct([('Id', pa.string()), ('Name', pa.string()), ('Age', pa.string())])
SCHEMA = pa.schema([("column1", COLUMN1_SCHEMA), ('column2', pa.int32())])

myschema = pa.schema([
    ("ogCarbs_hr", pa.float64()),
    ("carbs_hr", pa.string())
])

col_profile.aggregate_pandas_all([
    {'$match': {}},
    {'$project': {
        'ogCarbRatios': '$store.Alma.carbratio',
        'carbRatios': '$store.Default.carbratio',
        'isp': '$store.Default.sens',
        'ogCarbs_hr': '$store.Alma.carbs_hr',
        'carbs_hr': '$store.Default.carbs_hr',
        'startDate': '$startDate',
        'Default': '$defaultProfile'
    }}
],
    schema=myschema
)
