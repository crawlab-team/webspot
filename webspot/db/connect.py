import os

from mongoengine import connect as mongo_connect


def connect():
    conn_str = get_connection_str()
    mongo_connect(host=conn_str)


def get_connection_str():
    if os.environ.get('WEBSPOT_DATABASE_URL'):
        return os.environ.get('WEBSPOT_DATABASE_URL')
    return 'mongodb://localhost:27017/webspot'
