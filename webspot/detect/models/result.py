from typing import Dict, Any, Optional

from pydantic import BaseModel

from webspot.detect.models.selector import Selector


class Result(BaseModel):
    name: Optional[str]
    selectors: Optional[Dict[str, Selector]]
    score: Optional[float]
    scores: Optional[Dict[str, Optional[float]]]
    detector: Optional[str]
