from typing import Union

from sqlalchemy.orm import Session

from webspot.db.engine import get_engine

_session: Union[Session, None] = None


def get_session():
    global _session
    if _session is None or _session.is_active is False:
        _session = Session(bind=get_engine())
    return _session
