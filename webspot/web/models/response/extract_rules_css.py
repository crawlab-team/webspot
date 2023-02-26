from typing import List, Union

from pydantic import BaseModel


class ExtractRulesCssResponse(BaseModel):
    list: Union[str, None]
    items: Union[str, None]
    items_full: Union[str, None]
    fields: Union[List[dict], None]
    data: Union[List[dict], None]
