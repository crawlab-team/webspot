from typing import List, Union

from pydantic import BaseModel

from webspot.web.models.response.list_result import ListResultResponse


class RequestResponse(BaseModel):
    url: str
    method: str
    status: str
    html: Union[str, None]
    html_highlighted: Union[str, None]
    results: Union[List[ListResultResponse], None]
    valid: bool
    error: Union[str, None]
    no_async: bool
