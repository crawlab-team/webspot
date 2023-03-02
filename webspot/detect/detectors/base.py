from abc import abstractmethod
from typing import List

from webspot.detect.models.result import Result
from webspot.graph.graph_loader import GraphLoader
from webspot.request.html_requester import HtmlRequester


class BaseDetector(object):
    def __init__(
        self,
        graph_loader: GraphLoader,
        html_requester: HtmlRequester,
    ):
        # graph loader
        self.graph_loader = graph_loader

        # html requester
        self.html_requester = html_requester

        # results
        self.results: List[Result] = []

    @abstractmethod
    def highlight_html(self, html: str, **kwargs) -> str:
        pass

    @abstractmethod
    def run(self):
        pass
