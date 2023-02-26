from typing import Union

from pydantic import BaseModel, Field


class RequestPayload(BaseModel):
    url: str = Field(
        ...,
        title='URL',
        description='The URL to request.',
    )
    method: Union[str, None] = Field(
        default='request',
        title='Request Method',
        description='The method to use to request the page. (request, rod)',
    )
    no_async: Union[bool, None] = Field(
        default=False,
        title='No Async',
        description='If true, the request will be run synchronously, and return the result immediately.',
    )
    duration: Union[int, None] = Field(
        default=3,
        title='Duration (seconds)',
        description='The duration to request the page (method "rod" only)',
    )
