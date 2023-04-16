from typing import Optional

from pydantic import BaseModel


class Link(BaseModel):
    url: Optional[str]
    text: Optional[str]


class LinkListResult(BaseModel):
    name: Optional[str]
    list: Optional[list[Link]]
    confidence: Optional[float]
