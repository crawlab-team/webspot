import base64
import json
import logging
import os.path
import time
import traceback
from typing import List, Set

import html_to_json_enhanced
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from scipy.stats import entropy
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize

from webspot.graph.graph_loader import GraphLoader
from webspot.detect.utils.highlight_html import highlight_html
from webspot.detect.models.field import Field
from webspot.detect.models.list_result import ListResult
from webspot.detect.utils.transform_html_links import transform_html_links
from webspot.request.get_html import get_html


class PlainListDetector(object):
    def __init__(
        self,
        url: str = None,
        json_data: str = None,
        json_path: str = None,
        html_path: str = None,
        save_path: str = None,
        dbscan_eps: float = 0.5,
        dbscan_min_samples: int = 3,
        dbscan_metric: str = 'euclidean',
        entropy_threshold: float = 1e-3,
        embed_walk_length: int = 5,
        item_nodes_samples: int = 5,
        node2vec_ratio: float = 1.,
        request_method: str = 'request',
        request_rod_url: str = 'http://localhost:7777/request',
    ):
        # settings
        self.url = url
        self.json_data = json_data
        self.json_path = json_path
        self.html_path = html_path
        self.entropy_threshold = entropy_threshold
        self.item_nodes_samples = item_nodes_samples
        self.node2vec_ratio = node2vec_ratio
        self.request_method = request_method
        self.request_rod_url = request_rod_url

        # validate
        if not self.url:
            if self.json_path:
                assert self.html_path, 'html_path is required if json_path is provided and url is not provided'
            else:
                assert self.json_data, 'json_data is required if json_path is not provided and url is not provided'

        # save path
        self.save_path = save_path
        if not self.save_path:
            if self.url:
                self.save_path = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'detect', 'plain_list',
                                 self.url.replace('/', '_').replace(':', '_').replace('.', '_') + '.json'))
            elif self.json_path:
                self.save_path = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'detect', 'plain_list',
                                 self.json_path.split('/')[-1]))

        # data
        self._html = None

        # request html page if url exists
        if self.url:
            self._request()
        else:
            with open(self.html_path, 'r') as f:
                self._html = f.read()

        # graph loader
        self.graph_loader = GraphLoader(json_data=self.json_data, json_path=self.json_path,
                                        embed_walk_length=embed_walk_length)
        self.graph_loader.run()

        # dbscan clustering model
        self.dbscan = DBSCAN(
            metric=dbscan_metric,
            eps=dbscan_eps,
            min_samples=dbscan_min_samples,
        )

        # data
        self.results: List[ListResult] = []

    @property
    def html(self):
        html = self._html
        html = transform_html_links(html, self.url)
        html = highlight_html(html, self.results)
        return html

    @property
    def html_base64(self):
        return base64.b64encode(self.html.encode('utf-8')).decode('utf-8')

    @property
    def results_base64(self):
        return base64.b64encode(json.dumps(self.results).encode('utf-8')).decode('utf-8')

    def _request(self):
        self._html = get_html(self.url, self.request_method, self.request_rod_url)
        self.json_data = html_to_json_enhanced.convert(self._html, with_id=True)

    def _get_nodes_features_tags_attrs(self, nodes_idx: np.ndarray = None):
        """
        nodes features (tags + attributes)
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

    def _get_nodes_features_node2vec(self, nodes_idx: np.ndarray = None):
        """
        nodes features (node2vec)
        """
        if nodes_idx is None:
            embedded_tensor = self.graph_loader.nodes_embedded_tensor
        else:
            embedded_tensor = self.graph_loader.nodes_embedded_tensor[nodes_idx.T[0]]

        embedded_features_tensor = self.graph_loader.nodes_features_tensor[embedded_tensor].sum(dim=1)
        embedded_features = embedded_features_tensor.detach().numpy()

        return normalize(
            embedded_features,
            norm='l1',
            axis=1,
        )

    def _get_nodes_features(self, nodes_idx: np.ndarray = None):
        """
        nodes features (tags + attributes + node2vec)
        """
        x1 = self._get_nodes_features_tags_attrs(nodes_idx)
        x2 = self._get_nodes_features_node2vec(nodes_idx) * self.node2vec_ratio
        return normalize(
            np.concatenate(
                (x1, x2),
                axis=1,
            ),
            norm='l2',
            axis=1,
        )

    def _extract_fields_by_id(self, list_id: int) -> List[Field]:
        fields: List[Field] = []
        fields_extract_rules_set: Set[str] = set()
        list_child_nodes = self.graph_loader.get_node_children_by_id(list_id)
        for i, c in enumerate(list_child_nodes):
            if i == self.item_nodes_samples:
                break
            item_child_nodes = self.graph_loader.get_node_children_recursive_by_id(c.id)
            for n in item_child_nodes:
                if n.text is not None and n.text.strip() != '':
                    extract_rule_css = self.graph_loader.get_node_css_selector_path(node=n, root_id=list_id,
                                                                                    numbered=False)
                    fields_extract_rules_set.add(extract_rule_css)

        for i, extract_rule_css in enumerate(fields_extract_rules_set):
            fields.append(Field({
                'name': f'Field {i + 1}',
                'selector': extract_rule_css,
            }))
        return fields

    @staticmethod
    def _extract_data(soup: BeautifulSoup, items_selector_full: str, fields: List[Field]):
        data = []
        for item_el in soup.select(items_selector_full):
            row = {}
            for f in fields:
                try:
                    row[f.name] = item_el.select_one(f.selector).text.strip()
                except Exception as e:
                    # logging.warning(e)
                    continue
            data.append(row)
        return data

    def _train(self):
        self.dbscan.fit(self._get_nodes_features())

    def _filter(self):
        df_nodes = pd.DataFrame({
            'id': [n.id for n in self.graph_loader.nodes_],
            'parent_id': [n.parent_id for n in self.graph_loader.nodes_],
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
            # item node ids
            item_nodes_ids = df_nodes[df_nodes.label == label].id.values

            # item nodes
            item_nodes = self.graph_loader.get_nodes_by_ids(item_nodes_ids)

            # list node
            list_node = self.graph_loader.get_node_by_id(item_nodes[0].parent_id)

            # entropy
            entropy_ = df_labels.loc[label].entropy

            # add to result
            self.results.append(
                ListResult({
                    'nodes': {
                        'list': list_node,
                        'items': item_nodes,
                    },
                    'stats': {
                        'entropy': entropy_,
                    },
                }),
            )

    def _sort(self):
        for i, result in enumerate(self.results):
            nodes_ids = np.array([n.id for n in result.item_nodes])
            nodes_idx = np.argwhere(np.isin(self.graph_loader.nodes_ids, nodes_ids))

            try:
                nodes_features_vec = self._get_nodes_features(nodes_idx)
                nodes_features_vec_norm = normalize(nodes_features_vec.sum(axis=0).reshape(1, -1), norm='l1')
                score = entropy(nodes_features_vec_norm, axis=1)[0]
            except ValueError as e:
                # logging.warning(f'ValueError: {e}')
                score = 0

            self.results[i]['stats']['score'] = float(score)

        self.results = sorted(self.results, key=lambda x: x.stats.score, reverse=True)

        # assign name
        for i, result in enumerate(self.results):
            self.results[i]['name'] = f'List {i + 1}'

    def _extract(self):
        soup = BeautifulSoup(self._html, features='lxml')

        for i, result in enumerate(self.results):
            # list node
            list_node = result.list_node

            # item nodes
            item_nodes = result.item_nodes

            # list node extract rule (css)
            list_node_extract_rule_css = self.graph_loader.get_node_css_selector_path(list_node)

            # items node extract rule (css)
            items_node_extract_rule_css = self.graph_loader.get_node_css_selector_repr(item_nodes[0], False)

            # items node full extract rule (css)
            items_node_extract_rule_css_full = f'{list_node_extract_rule_css} > {items_node_extract_rule_css}'

            # fields node extract rule
            fields_node_extract_rule_css = self._extract_fields_by_id(list_node.id)

            # data
            data = self._extract_data(soup, items_node_extract_rule_css_full, fields_node_extract_rule_css)

            self.results[i]['extract_rules_css'] = {
                'list': list_node_extract_rule_css,
                'items': items_node_extract_rule_css,
                'items_full': items_node_extract_rule_css_full,
                'fields': fields_node_extract_rule_css,
                'data': data,
            }

    def _save(self):
        if not os.path.exists(os.path.dirname(self.save_path)):
            os.makedirs(os.path.dirname(self.save_path))

        with open(self.save_path, 'w') as f:
            f.write(json.dumps(self.results, indent=2))

    def run(self):
        tic = time.time()

        # train clustering model
        self._train()

        # filter nodes
        self._filter()

        # sort results
        self._sort()

        # extract fields into results
        self._extract()

        # save results
        self._save()

        toc = time.time()
        logging.info(f'PlainListExtractor: {toc - tic:.2f}s')

        return self.results


if __name__ == '__main__':
    data_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/quotes.toscrape.com/json/http___quotes_toscrape_com_.json'
    # data_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/github.com/json/https___github_com_trending.json'
    # data_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/news.ycombinator.com/json/https___news_ycombinator_com.json'
    # data_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/www.ruanyifeng.com/json/http___www_ruanyifeng_com_blog_.json'
    # data_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/www.producthunt.com/json/https___www_producthunt_com.json'
    # data_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/edition.cnn.com/json/https___edition_cnn_com.json'
    # data_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/shixian.com/json/https___shixian_com_jobs_part-time.json'
    # data_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/github.com/json/https___github_com_search?q=crawlab.json'
    # detector = PlainListDetector(json_path=data_path)

    # url = 'https://quotes.toscrape.com/'
    # url = 'https://cuiqingcai.com/'
    url = 'https://cuiqingcai.com/archives/'
    detector = PlainListDetector(url=url)

    detector.run()

    for result in detector.results:
        print(result.extract_rules)
        # n = detector.graph_loader.get_node_by_id(result.list_node.id)
