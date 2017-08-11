from google.cloud import datastore
import simplejson as json
from datetime import datetime


def get_unix_timestamp(timestamp):
    if isinstance(timestamp, int):
        return timestamp

    if isinstance(timestamp, str):
        utc_dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
        # convert to unix timestamp
        return int((utc_dt - datetime(1970, 1, 1)).total_seconds())


def migration_date_to_unix_timestamp():

    client = datastore.Client()
    query = client.query(kind='Channels')
    query.order = ['date']
    datastore_entities = list(query.fetch(limit=500))
    num_entities = len(datastore_entities)

    while num_entities > 0:

        for datastore_entity in datastore_entities:

            if 'date' in datastore_entity:
                datastore_entity['timestamp'] = get_unix_timestamp(datastore_entity['date'])
                del datastore_entity['date']
                client.put(datastore_entity)

        client = datastore.Client()
        query = client.query(kind='Channels')
        query.order = ['date']
        datastore_entities = list(query.fetch(limit=500))
        num_entities = len(datastore_entities)
