from typing import List, Union

from pydantic import BaseModel

from webspot.detect.models.stats import Stats
from webspot.web.models.response.extract_rules_css import ExtractRulesCssResponse


class ListResultResponse(BaseModel):
    name: Union[str, None]
    nodes: Union[dict, None]
    stats: Union[Stats, None]
    extract_rules_css: Union[ExtractRulesCssResponse, None]
