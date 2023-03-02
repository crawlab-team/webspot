from typing import List

from webspot.detect.models.result import Result
from webspot.detect.models.selector import Selector


class ListResult(Result):
    fields: List[Selector]
    data: List[dict]
