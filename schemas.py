from pymongoarrow.api import Schema


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

    return treatments_schema, entries_schema
