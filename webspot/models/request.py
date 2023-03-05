from typing import List, Optional, Dict, Union

from mongoengine import StringField, BooleanField, ListField, IntField, DictField

from webspot.constants.detector import DETECTOR_PLAIN_LIST, DETECTOR_PAGINATION
from webspot.constants.html_request_method import HTML_REQUEST_METHOD_REQUEST
from webspot.constants.request_status import REQUEST_STATUS_PENDING
from webspot.detect.models.list_result import ListResult
from webspot.detect.models.result import Result
from webspot.models.base import Base, BaseOut


class RequestOut(BaseOut):
    url: str
    method: Optional[str]
    duration: Optional[int]
    status: Optional[str]
    results: Optional[Dict[str, List[Union[ListResult, Result]]]]
    valid: Optional[bool]
    error: Optional[str]
    no_async: Optional[bool]
    detectors: List[str]
    execution_time: Optional[dict]


class Request(Base):
    meta = {'allow_inheritance': True}

    url = StringField()
    method = StringField(default=HTML_REQUEST_METHOD_REQUEST)
    duration = IntField()
    status = StringField(default=REQUEST_STATUS_PENDING)
    html = StringField()
    html_highlighted = StringField()
    results = DictField(default={})
    valid = BooleanField(default=True)
    error = StringField()
    no_async = BooleanField(default=False)
    detectors = ListField(default=[DETECTOR_PLAIN_LIST, DETECTOR_PAGINATION])
    execution_time = DictField(default={})

    def to_out(self) -> BaseOut:
        return RequestOut(
            id=str(self.id),
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
            url=self.url,
            method=self.method,
            duration=self.duration,
            status=self.status,
            html=self.html,
            html_highlighted=self.html_highlighted,
            results=self.results,
            valid=self.valid,
            error=self.error,
            no_async=self.no_async,
            detectors=self.detectors,
            execution_time=self.execution_time,
        )
