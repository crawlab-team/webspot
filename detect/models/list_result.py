from typing import List

from detect.models.stats import Stats
from models.node import Node


class ListResult(dict):
    @property
    def item_nodes(self) -> List[Node]:
        return self.get('nodes').get('items')

    @property
    def list_node(self) -> Node:
        return self.get('nodes').get('list')

    @property
    def stats(self) -> Stats:
        return Stats(self.get('stats') or {})

    @property
    def extract_rules(self):
        return {
            'list': self.get('extract_rules_css').get('list'),
            'items': self.get('extract_rules_css').get('items'),
        }
