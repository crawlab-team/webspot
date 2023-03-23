from typing import Optional

from pydantic import BaseModel


class Selector(BaseModel):
    name: str
    selector: str
    type: Optional[str]
    attribute: Optional[str]
