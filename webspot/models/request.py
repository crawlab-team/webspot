from typing import Union, Optional, List

from pydantic import BaseModel
from mongoengine import StringField, BooleanField, ListField, IntField

from webspot.constants.html_request_method import HTML_REQUEST_METHOD_REQUEST
from webspot.constants.request_status import REQUEST_STATUS_PENDING
from webspot.detect.models.list_result import ListResult
from webspot.models.base import Base


class Request(Base):
    meta = {'allow_inheritance': True}

    url = StringField()
    method = StringField(default=HTML_REQUEST_METHOD_REQUEST)
    duration = IntField()
    status = StringField(default=REQUEST_STATUS_PENDING)
    html = StringField()
    html_highlighted = StringField()
    results = ListField()
    valid = BooleanField(default=True)
    error = StringField()
    no_async = BooleanField(default=False)


class RequestIn(BaseModel):
    url: str
    method: str
    status: str
    html: Optional[str]
    html_highlighted: Optional[str]
    results: Optional[List[ListResult]]
    valid: bool
    error: Optional[str]
    no_async: bool


class RequestOut(RequestIn):
    _id: str
