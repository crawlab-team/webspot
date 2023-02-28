from mongoengine import StringField, BooleanField, ListField, DictField

from webspot.constants.detector import DETECTOR_PLAIN_LIST, DETECTOR_PAGINATION
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
    results = DictField(default={})
    valid = BooleanField(default=True)
    error = StringField()
    no_async = BooleanField(default=False)
    detectors = ListField(default=[DETECTOR_PLAIN_LIST, DETECTOR_PAGINATION])
