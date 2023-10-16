from pymongoarrow.api import Schema
# from pymongoarrow.types import list_
import pyarrow as pa
import numpy as np


def mdb_schemas():
    entries_schema = Schema({
        'sgv': float,
        'dateString': str,
    })

    treatments_schema = Schema({
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

    devicestatus_schema = Schema({
        'created_at': str,
        'override': {'active': bool},
        'loop': {
            'predicted': {'values': pa.list_(pa.float64())},
            'enacted': {'duration': float,
                        'rate': float,
                        'bolusVolume': float,
                        'received': bool},
            'recommendedBolus': float,
            'automaticDoseRecommendation': {'bolusVolume': float},
            'cob': float,
            'iob': {'iob': float}
        }
    })

    return treatments_schema, entries_schema, devicestatus_schema, profile_schema

