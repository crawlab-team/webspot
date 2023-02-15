import logging
import os
from typing import Union

from sqlalchemy import create_engine, Engine

from webspot.models.base import Base

_engine: Union[Engine, None] = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(get_connection_str(), echo=True)
        _create_tables(_engine)
    return _engine


def _create_tables(engine: Engine = None):
    if engine is None:
        engine = get_engine()
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logging.warning(e)


def get_connection_str():
    if os.environ.get('WEBSPOT_DATABASE_URL'):
        return os.environ.get('WEBSPOT_DATABASE_URL')
    return 'sqlite:///webspot.db'
