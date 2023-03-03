from typing import Optional, List

from webspot.detect.models.result import Result


class TableResult(Result):
    columns: Optional[List[str]]
    data: Optional[List[dict]]
