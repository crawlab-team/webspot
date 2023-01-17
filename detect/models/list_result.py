from typing import List

from models.node import Node


class ListResult(dict):
    @property
    def nodes(self) -> List[Node]:
        return self.get('nodes')

    @property
    def container(self) -> Node:
        return self.get('container')

    @property
    def entropy(self) -> float:
        return self.get('entropy')
