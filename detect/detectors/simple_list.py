import json
import logging
import os.path
from typing import List

import numpy as np
import pandas as pd
from scipy.stats import entropy
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize

from dataset.graph_loader import GraphLoader
from detect.models.list_result import ListResult


class SimpleListDetector(object):
    def __init__(self, data_path: str, save_path: str = None, dbscan_eps: float = 0.5, dbscan_min_samples: int = 5,
                 entropy_threshold: float = 1e-3, embed_walk_length: int = 5):
        # settings
        self.entropy_threshold = entropy_threshold
        self.save_path = save_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'detect', 'simple_list',
                         data_path.split('/')[-1]))

        # graph loader
        self.graph_loader = GraphLoader(data_path, embed_walk_length=embed_walk_length)
        self.graph_loader.run()

        # dbscan clustering model
        self.dbscan = DBSCAN(eps=dbscan_eps, min_samples=dbscan_min_samples)

        # data
        self.results: List[ListResult] = []

    def _get_nodes_features_tags_attrs(self, nodes_idx: np.ndarray = None):
        """
        nodes features (tags + attributes)
        """
        if nodes_idx is None:
            features = self.graph_loader.nodes_features_tensor.detach().numpy()
        else:
            features = self.graph_loader.nodes_features_tensor.detach().numpy()[nodes_idx].sum(axis=1)

        return normalize(features, norm='l1', axis=1)

    def _get_nodes_features_node2vec(self, nodes_idx: np.ndarray = None):
        """
        nodes features (node2vec)
        """
        if nodes_idx is None:
            features = self.graph_loader.nodes_features_tensor.detach().numpy()
        else:
            features = self.graph_loader.nodes_features_tensor.detach().numpy()[nodes_idx].sum(axis=1)

        return normalize(
            features,
            norm='l1',
            axis=1,
        )

    def _get_nodes_features(self, nodes_idx: np.ndarray = None):
        """
        nodes features (tags + attributes + node2vec)
        """
        return normalize(
            np.concatenate(
                (self._get_nodes_features_tags_attrs(nodes_idx), self._get_nodes_features_node2vec(nodes_idx)),
                axis=1,
            ),
            norm='l2',
            axis=1,
        )

    def _train(self):
        self.dbscan.fit(self._get_nodes_features())

    def _filter(self):
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

        threshold_mask = df_labels.entropy < self.entropy_threshold
        df_labels_filtered = df_labels[threshold_mask]

        for label in df_labels_filtered.index:
            nodes_ids = df_nodes[df_nodes.label == label].id.values
            nodes = self.graph_loader.get_nodes_by_ids(nodes_ids)
            root = self.graph_loader.get_node_by_id(nodes[0].parent_id)
            entropy_ = df_labels.loc[label].entropy
            self.results.append(
                ListResult({
                    'root': root,
                    'nodes': nodes,
                    'stats': {
                        'entropy': entropy_,
                    },
                }),
            )

    def _sort(self):
        for i, result in enumerate(self.results):
            nodes_ids = np.array([n.id for n in result.nodes])
            nodes_idx = np.argwhere(np.isin(self.graph_loader.nodes_ids, nodes_ids))

            try:
                nodes_features_vec = self._get_nodes_features(nodes_idx)
                nodes_features_vec_norm = normalize(nodes_features_vec.sum(axis=0).reshape(1, -1), norm='l1')
                score = entropy(nodes_features_vec_norm, axis=1)[0]
            except ValueError as e:
                logging.warning(f'ValueError: {e}')
                score = 0

            self.results[i]['stats']['score'] = float(score)

        self.results = sorted(self.results, key=lambda x: x.stats.score, reverse=True)

    def _save(self):
        if not os.path.exists(os.path.dirname(self.save_path)):
            os.makedirs(os.path.dirname(self.save_path))

        with open(self.save_path, 'w') as f:
            f.write(json.dumps(self.results, indent=2))

    def run(self):
        # train clustering model
        self._train()

        # filter nodes
        self._filter()

        # sort results
        self._sort()

        # save results
        self._save()

        return self.results


if __name__ == '__main__':
    data_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/quotes.toscrape.com/json/http___quotes_toscrape_com_.json'
    # data_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/docs.scrapy.org/json/https___docs_scrapy_org_en_latest_.json'
    # data_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/news.ycombinator.com/json/https___news_ycombinator_com.json'
    # data_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/ssr1.scrape.center/json/https___ssr1_scrape_center.json'
    # data_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/github.com/json/https___github_com_trending.json'
    detector = SimpleListDetector(data_path, dbscan_eps=0.5, dbscan_min_samples=4)
    detector.run()
