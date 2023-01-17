import json
from typing import List

import numpy as np
import pandas as pd
import torch
from scipy.stats import entropy
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize

from dataset.graph_loader import GraphLoader
from detect.models.list_result import ListResult
from models.node import Node


class SimpleListDetector(object):
    def __init__(self, graph_loader: GraphLoader, dbscan_eps: float = 0.5, dbscan_min_samples: int = 5,
                 entropy_threshold: float = 0.5):
        # settings
        self.ent_threshold = entropy_threshold

        # graph loader
        self.graph_loader = graph_loader
        self.graph_loader.run()

        # dbscan clustering model
        self.dbscan = DBSCAN(eps=dbscan_eps, min_samples=dbscan_min_samples)

    def _get_nodes_features_tags_attrs(self):
        """
        nodes features (tags + attributes)
        """
        return normalize(self.graph_loader.nodes_features_tensor.detach().numpy(), norm='l1', axis=1)

    def _get_nodes_features_node2vec(self):
        """
        nodes features (node2vec)
        """
        return normalize(
            self.graph_loader.nodes_features_tensor[self.graph_loader.nodes_embedded_tensor]
            .sum(dim=1)
            .detach().numpy(),
            norm='l1',
            axis=1,
        )

    def _get_nodes_features(self):
        return normalize(
            np.concatenate(
                (self._get_nodes_features_tags_attrs(), self._get_nodes_features_node2vec()),
                axis=1,
            ),
            norm='l2',
            axis=1,
        )

    def _train(self):
        self.dbscan.fit(self._get_nodes_features())

    def _filter(self) -> List[ListResult]:
        df_nodes = pd.DataFrame({
            'id': [n.id for n in self.graph_loader.nodes],
            'parent_id': [n.parent_id for n in self.graph_loader.nodes],
            'label': self.dbscan.labels_,
        })
        df_nodes = df_nodes[df_nodes.label != -1]

        df_labels = df_nodes \
            .groupby('label')[['parent_id']] \
            .agg(lambda s: entropy(s.value_counts())) \
            .rename(columns={'parent_id': 'entropy'}) \
            .sort_values(by='entropy', ascending=True)

        threshold_mask = df_labels.entropy < self.ent_threshold

        res: List[ListResult] = []
        for label in df_labels[threshold_mask].index:
            nodes_ids = df_nodes[df_nodes.label == label].id.values
            nodes = self.graph_loader.get_nodes_by_ids(nodes_ids)
            container = self.graph_loader.get_node_by_id(nodes[0].parent_id)
            entropy_ = df_labels.iloc[label].entropy
            res.append(
                ListResult({
                    'container': container,
                    'nodes': nodes,
                    'entropy': entropy_,
                }),
            )

        return res

    def detect(self) -> List[ListResult]:
        # train clustering model
        self._train()

        # filter nodes
        return self._filter()


if __name__ == '__main__':
    # data_path = '/Users/marvzhang/projects/crawlab-team/auto-html/data/quotes.toscrape.com/json/http___quotes_toscrape_com_.json'
    data_path = '/Users/marvzhang/projects/crawlab-team/auto-html/data/docs.scrapy.org/json/https___docs_scrapy_org_en_latest_.json'
    graph_loader = GraphLoader(data_path=data_path)
    detector = SimpleListDetector(graph_loader, dbscan_eps=0.8, dbscan_min_samples=4, entropy_threshold=0.5)
    results = detector.detect()
    print(json.dumps(results))
