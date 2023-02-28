from typing import List, Dict, Any, Optional

from pydantic import BaseModel

from webspot.detect.models.selector import Selector
from webspot.detect.models.stats import Stats
from webspot.graph.models.node import Node


class Result(BaseModel):
    name: Optional[str]
    selectors: Optional[Dict[str, Selector]]
    score: Optional[float]
    scores: Optional[Dict[str, Optional[float]]]
