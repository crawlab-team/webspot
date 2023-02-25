from typing import Union

from mongoengine import connect
from sqlalchemy.orm import Session

from webspot.db.engine import get_connection_str

_session: Union[Session, None] = None


def get_session():
    conn_str = get_connection_str()
    connect(host=conn_str)
