import logging
import os
from typing import Union

from sqlalchemy import create_engine, Engine

_engine: Union[Engine, None] = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(get_connection_str(), echo=True)
    return _engine


def get_connection_str():
    if os.environ.get('WEBSPOT_DATABASE_URL'):
        return os.environ.get('WEBSPOT_DATABASE_URL')
    return 'mongodb://localhost:27017/webspot'
