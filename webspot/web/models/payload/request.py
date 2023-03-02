from typing import Optional, List

from pydantic import BaseModel, Field

from webspot.constants.detector import DETECTOR_PLAIN_LIST, DETECTOR_PAGINATION


class RequestPayload(BaseModel):
    url: str = Field(
        ...,
        title='URL',
        description='The URL to request.',
    )
    method: Optional[str] = Field(
        default='request',
        title='Request Method',
        description='The method to use to request the page. (request, rod)',
    )
    no_async: Optional[bool] = Field(
        default=False,
        title='No Async',
        description='If true, the request will be run synchronously, and return the result immediately.',
    )
    detectors: Optional[List[str]] = Field(
        default=[DETECTOR_PLAIN_LIST, DETECTOR_PAGINATION],
        title='Detectors',
        description='The detectors to run on the page.',
    )
    duration: Optional[int] = Field(
        default=3,
        title='Duration (seconds)',
        description='The duration to request the page (method "rod" only)',
    )
