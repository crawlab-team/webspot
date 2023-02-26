from abc import abstractmethod

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

    @abstractmethod
    def run(self):
        pass
