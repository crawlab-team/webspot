from mongoengine import connect as mongo_connect

from webspot.db.engine import get_connection_str


def connect():
    conn_str = get_connection_str()
    mongo_connect(host=conn_str)
