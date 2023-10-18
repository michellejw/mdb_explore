"""load_data.py
Import Loop data from a mongodB/Atlas database.
"""
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import yaml

# Pyarrow - importing mongo databases into pandas
import pymongoarrow.monkey
from mdb_tools.schemas import mdb_schemas
# import pyarrow as pa
# from pymongoarrow.api import Schema

# Add extra find_* methods to pymongo collection objects (pymongoarrow):
pymongoarrow.monkey.patch_all()


def get_collections(yml_secrets_file):
    """
    Using the URI for the mongodb database, load a set of collections (the selection is currently hard-coded

    Example usage:
    col_entries, col_treatments, col_profile, col_device_status = ld.get_collections(yml_secrets_file)

    Args:
        yml_secrets_file (str): path to a yml file containing the URI and mongodB name.

    Returns: A tuple containing a specific set of collections (basically, tables, from the mongo database: entries, treatments, profile, and device status, in that order.

    """

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

    return col_entries, col_treatments, col_profile, col_devicestatus


def get_entries_df(col_entries0):
    """
    Using pyarrow, extract all of the documents in the entries collection and construct a Pandas dataframe from a subset of them.

    Args:
        col_entries0: A MongoDB collection containing information from the CGM (continuous glucose monitor).

    Returns: a Pandas dataframe containing information from the entries collection

    """
    _, entries_schema, _, _ = mdb_schemas()

    return col_entries0.find_pandas_all({}, schema=entries_schema)


def get_treatments_df(col_treatments0):
    """
    Using pyarrow, extract all of the documents in the treatments collection and construct a Pandas dataframe from a subset of them.

    Args:
        col_treatments0: A MongoDB collection containing treatment information from the pump (boluses, temp basals, corrections, etc)

    Returns: a Pandas dataframe containing information from the treatments collection

    """
    treatment_schema, _, _, _ = mdb_schemas()

    return col_treatments0.find_pandas_all({}, schema=treatment_schema)


def get_devicestatus_df(col_devicestatus0):
    """
    Using pyarrow, extract all of the documents in the devicestatus collection and construct a Pandas dataframe from a subset of them.

    Args:
        col_devicestatus0: A MongoDB collection containing status information from the pump.

    Returns: a Pandas dataframe containing information from the device status collection

    """
    _, _, devicestatus_schema, _ = mdb_schemas()

    return col_devicestatus0.find_pandas_all({}, schema=devicestatus_schema)
