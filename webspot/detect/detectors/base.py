from abc import abstractmethod
from typing import List

import numpy as np

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

    def get_nodes_idx_by_feature(self, feature_key: str, feature_value: str):
        feature = f'{feature_key}={feature_value}'
        feature_tag_a_idx = np.argwhere(np.array(self.graph_loader.nodes_features_enc.feature_names_) == feature)[0]
        return np.argwhere(self.graph_loader.nodes_features_tensor[:, feature_tag_a_idx].T[0] == 1)[0].detach().numpy()

    def get_nodes_by_feature(self, feature_key: str, feature_value: str):
        nodes_idx = self.get_nodes_idx_by_feature(feature_key, feature_value)
        return [n for n in self.graph_loader.nodes[nodes_idx]]

    @abstractmethod
    def highlight_html(self, html: str, **kwargs) -> str:
        pass

    @abstractmethod
    def run(self):
        pass
