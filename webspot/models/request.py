from mongoengine import StringField, BooleanField, ListField

from webspot.constants.html_request_method import HTML_REQUEST_METHOD_REQUEST
from webspot.constants.request_status import REQUEST_STATUS_PENDING
from webspot.models.base import Base


class Request(Base):
    meta = {'allow_inheritance': True}

    url = StringField()
    method = StringField(default=HTML_REQUEST_METHOD_REQUEST)
    status = StringField(default=REQUEST_STATUS_PENDING)
    html = StringField()
    html_highlighted = StringField()
    results = ListField()
    valid = BooleanField(default=True)
    error = StringField()
