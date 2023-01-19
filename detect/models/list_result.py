from typing import List

from detect.models.stats import Stats
from models.node import Node


class ListResult(dict):
    @property
    def nodes(self) -> List[Node]:
        return self.get('nodes')

    @property
    def root(self) -> Node:
        return self.get('root')

    @property
    def stats(self) -> Stats:
        return Stats(self.get('stats') or {})
