import base64
import json
import time
from typing import List, Set, Dict
from urllib.parse import urljoin

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from scipy.sparse import csr_matrix
from scipy.stats import entropy
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize

from webspot.constants.detector import DETECTOR_PLAIN_LIST
from webspot.constants.field_extract_rule_type import FIELD_EXTRACT_RULE_TYPE_TEXT, FIELD_EXTRACT_RULE_TYPE_LINK_URL, \
    FIELD_EXTRACT_RULE_TYPE_IMAGE_URL
from webspot.detect.detectors.base import BaseDetector
from webspot.detect.models.selector import Selector
from webspot.detect.utils.math import log_positive
from webspot.detect.utils.highlight_html import add_class, add_label
from webspot.detect.models.list_result import ListResult
from webspot.graph.graph_loader import GraphLoader
from webspot.graph.models.node import Node
from webspot.logging import get_logger
from webspot.request.html_requester import HtmlRequester

logger = get_logger('webspot.detect.detectors.plain_list')


class PlainListDetector(BaseDetector):
    def __init__(
        self,
        dbscan_eps: float = 0.5,
        dbscan_min_samples: int = 3,
        dbscan_metric: str = 'euclidean',
        dbscan_n_jobs: int = -1,
        entropy_threshold: float = 1e-3,
        score_threshold: float = 1.,
        min_item_nodes: int = 5,
        node2vec_ratio: float = 1.,
        result_name_prefix: str = 'List',
        text_length_discount: float = 0.01,
        max_text_length: float = 1024,
        max_item_count: int = 10,
        max_feature_count: int = 10,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # settings
        self.entropy_threshold = entropy_threshold
        self.score_threshold = score_threshold
        self.min_item_nodes = min_item_nodes
        self.node2vec_ratio = node2vec_ratio
        self.result_name_prefix = result_name_prefix
        self.text_length_discount = text_length_discount
        self.max_text_length = max_text_length
        self.max_item_count = max_item_count
        self.max_feature_count = max_feature_count

        # dbscan model
        self.dbscan = DBSCAN(
            metric=dbscan_metric,
            eps=dbscan_eps,
            min_samples=dbscan_min_samples,
            n_jobs=dbscan_n_jobs,
        )

        # data
        self.results: List[ListResult] = []

    @property
    def _html(self):
        return self.graph_loader.html

    @property
    def url(self):
        return self.html_requester.url

    def highlight_html(self, html: str, **kwargs) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        for i, result in enumerate(self.results):
            # list
            list_selector = result.selectors.get('list')
            list_el = soup.select_one(list_selector.selector)
            if not list_el:
                continue
            add_class(list_el, ['webspot-highlight-container', 'webspot-highlight-node-color__blue'])
            add_label(list_el, soup, f'List {i + 1}', 'primary')

            # items
            items_selector = result.selectors.get('items')
            item_els = list_el.select(items_selector.selector)
            for j, item_el in enumerate(item_els):
                add_class(item_el, ['webspot-highlight-container', 'webspot-highlight-node-color__orange'])
                # _add_label(item_el, soup, f'Item {j + 1}', 'warning')

                # fields
                for k, field in enumerate(result.fields):
                    try:
                        field_els = item_el.select(field.selector)
                    except Exception as e:
                        # logging.warning(e)
                        field_els = []
                    for field_el in field_els:
                        add_class(field_el, ['webspot-highlight-container', 'webspot-highlight-node-color__green'])
                        # _add_label(field_el, soup, f'Field {k + 1}', 'success')
        return str(soup)

    @property
    def html(self):
        return self.highlight_html(self._html, )

    @property
    def html_base64(self):
        return base64.b64encode(self.html.encode('utf-8')).decode('utf-8')

    @property
    def results_base64(self):
        return base64.b64encode(json.dumps(self.results).encode('utf-8')).decode('utf-8')

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

    def _get_nodes_features(self, nodes_idx: np.ndarray = None, to_sparse: bool = False):
        """
        nodes features (tags + attributes + node2vec)
        """
        x1 = self._get_nodes_features_tags_attrs(nodes_idx)
        x2 = self._get_nodes_features_node2vec(nodes_idx) * self.node2vec_ratio
        x = normalize(
            np.concatenate(
                (x1, x2),
                axis=1,
            ),
            norm='l2',
            axis=1,
        )
        logger.debug(f'nodes features size: {x.shape}')

        if to_sparse:
            return csr_matrix(x)
        else:
            return x

    def _extract_fields_by_id(self, list_id: int, item_nodes: List[Node]) -> List[Selector]:
        # fields
        fields: List[Selector] = []

        # extract rules set (css selector path, type, attribute)
        fields_extract_rules_set: Set[(str, str)] = set()

        # list child nodes
        list_child_nodes = self.graph_loader.get_node_children_by_id(list_id)

        # iterate list child nodes
        i = 0
        for c in list_child_nodes:
            if c.tag != item_nodes[0].tag:
                continue

            # stop if item nodes samples reached
            if i == self.min_item_nodes:
                break

            # item child nodes
            item_child_nodes = self.graph_loader.get_node_children_recursive_by_id(c.id)

            # iterate item child nodes
            for n in item_child_nodes:
                # extract text
                if n.text is not None and n.text.strip() != '':
                    extract_rule_css = self.graph_loader.get_node_css_selector_path(node=n, root_id=list_id,
                                                                                    numbered=False, no_id=True)
                    fields_extract_rules_set.add((extract_rule_css, FIELD_EXTRACT_RULE_TYPE_TEXT, ''))

                # extract link
                if n.tag == 'a' and n.attrs.get('href') is not None:
                    extract_rule_css = self.graph_loader.get_node_css_selector_path(node=n, root_id=list_id,
                                                                                    numbered=False, no_id=True)
                    fields_extract_rules_set.add((extract_rule_css, FIELD_EXTRACT_RULE_TYPE_LINK_URL, 'href'))

                # extract image url
                if n.tag == 'img' and n.attrs.get('src') is not None:
                    extract_rule_css = self.graph_loader.get_node_css_selector_path(node=n, root_id=list_id,
                                                                                    numbered=False, no_id=True)
                    fields_extract_rules_set.add((extract_rule_css, FIELD_EXTRACT_RULE_TYPE_IMAGE_URL, 'src'))

            i += 1

        for i, item in enumerate(fields_extract_rules_set):
            extract_rule_css, type_, attribute = item
            name = f'Field_{type_}_{i + 1}'
            fields.append(Selector(
                name=name,
                selector=extract_rule_css,
                type=type_,
                attribute=attribute,
            ))
        return fields

    def _extract_data(self, soup: BeautifulSoup, items_selector_full: str, fields: List[Selector]):
        data = []
        for item_el in soup.select(items_selector_full):
            row = {}
            for f in fields:
                try:
                    field_el = item_el.select_one(f.selector)
                    if f.type == FIELD_EXTRACT_RULE_TYPE_TEXT:
                        row[f.name] = field_el.text.strip()
                    elif f.type == FIELD_EXTRACT_RULE_TYPE_LINK_URL:
                        row[f.name] = urljoin(self.url, field_el.attrs.get(f.attribute))
                    elif f.type == FIELD_EXTRACT_RULE_TYPE_IMAGE_URL:
                        row[f.name] = urljoin(self.url, field_el.attrs.get(f.attribute))
                    else:
                        continue
                except Exception as e:
                    # logging.warning(e)
                    continue
            data.append(row)
        return data

    def _train(self):
        self.dbscan.fit(self._get_nodes_features(to_sparse=True))

    def _pre_filter(self) -> (List[Node], List[List[Node]]):
        df_nodes = pd.DataFrame({
            'id': [n.id for n in self.graph_loader.nodes_],
            'parent_id': [n.parent_id for n in self.graph_loader.nodes_],
            'label': self.dbscan.labels_,
        })
        df_nodes_filtered = df_nodes[df_nodes.label != -1]
        logger.debug('nodes before pre-filter: %s' % df_nodes.shape[0])
        logger.debug('nodes after pre-filter: %s' % df_nodes_filtered.shape[0])

        df_labels = df_nodes_filtered \
            .groupby('label')[['parent_id']] \
            .agg(lambda s: entropy(s.value_counts())) \
            .rename(columns={'parent_id': 'entropy'}) \
            .sort_values(by='entropy', ascending=True)

        # threshold_mask = df_labels.entropy < self.entropy_threshold
        # df_labels_filtered = df_labels[threshold_mask]

        item_nodes_list = []
        list_node_list = []
        for label in df_labels.index:
            # item nodes (filtered by label only)
            df_nodes_filtered_by_label = df_nodes_filtered[df_nodes_filtered.label == label]

            # iterate parent id
            for parent_id in df_nodes_filtered_by_label.parent_id.unique().tolist():
                # item nodes (further filtered parent id)
                df_nodes_filtered_by_label_parent_id = df_nodes_filtered_by_label[
                    df_nodes_filtered.parent_id == parent_id]

                # skip if item nodes count is less than required
                if df_nodes_filtered_by_label_parent_id.shape[0] < self.min_item_nodes:
                    continue

                # item node ids
                item_nodes_ids = df_nodes_filtered_by_label_parent_id.id.values

                # item nodes
                item_nodes = self.graph_loader.get_nodes_by_ids(item_nodes_ids)
                item_nodes_list.append(item_nodes)

                # list node
                list_node = self.graph_loader.get_node_by_id(item_nodes[0].parent_id)
                list_node_list.append(list_node)

        return list_node_list, item_nodes_list

    def _filter(
        self,
        list_node_list: List[Node],
        item_nodes_list: List[List[Node]],
    ) -> (List[Node], List[List[Node]], List[float], List[Dict[str, float]]):
        score_list = []
        scores_list = []
        idx: List[int] = []
        for i, list_node, item_nodes in zip(range(len(list_node_list)), list_node_list, item_nodes_list):
            nodes_ids = np.random.choice(np.array([n.id for n in item_nodes]), size=10)
            try:
                score_text_richness = 0
                score_complexity = 0
                for node_id in nodes_ids:
                    child_nodes_idx = self.graph_loader.get_node_children_idx_recursive_by_id(node_id)
                    if len(child_nodes_idx) == 0:
                        continue
                    nodes_text_length_vec = self.graph_loader.nodes_text_length_vec[child_nodes_idx]
                    nodes_text_length_vec_non_zero = nodes_text_length_vec[nodes_text_length_vec > 0]
                    _score_text_richness = log_positive(
                        min(nodes_text_length_vec_non_zero.sum(), self.max_text_length) * self.text_length_discount)
                    _score_complexity = log_positive(min(len(nodes_text_length_vec_non_zero), self.max_feature_count))
                    if _score_text_richness > score_text_richness:
                        score_text_richness = _score_text_richness
                    if _score_complexity > score_complexity:
                        score_complexity = _score_complexity
                score_item_count = log_positive(min(len(item_nodes), self.max_item_count))

                logger.debug(f'score_text_richness: {score_text_richness}')
                logger.debug(f'score_complexity: {score_complexity}')
                logger.debug(f'score_item_count: {score_item_count}')

                # score
                score = score_text_richness + score_complexity + score_item_count
                logger.debug(f'score: {score}')

                # skip score less than threshold
                if score < self.score_threshold:
                    continue

                # skip zero sub-score
                if score_text_richness == 0 or score_complexity == 0 or score_item_count == 0:
                    continue

                # add to scores list
                scores_list.append({
                    'text_richness': score_text_richness,
                    'complexity': score_complexity,
                    'item_count': score_item_count,
                })

                # add to score list
                score_list.append(score)

                # add to idx
                idx.append(i)

            except ValueError as e:
                # logging.warning(f'ValueError: {e}')
                pass

        res_list_node_list = [list_node_list[i] for i in idx]
        res_item_nodes_list = [item_nodes_list[i] for i in idx]

        return res_list_node_list, res_item_nodes_list, score_list, scores_list

    def _extract(
        self,
        list_node_list: List[Node],
        item_nodes_list: List[List[Node]],
        score_list: List[float],
        scores_list: List[Dict[str, float]],
    ) -> List[ListResult]:
        # soup
        soup = BeautifulSoup(self._html, features='lxml')

        # results
        results = []

        # iterate inputs
        for i, list_node, item_nodes, score, scores in zip(range(len(list_node_list)),
                                                           list_node_list,
                                                           item_nodes_list,
                                                           score_list,
                                                           scores_list):
            # list node
            list_node = list_node

            # item nodes
            item_nodes = item_nodes

            # list selector
            list_selector = Selector(
                name='list',
                selector=self.graph_loader.get_node_css_selector_path(list_node),
                type='css',
            )

            # items node extract rule (css)
            items_selector = Selector(
                name='items',
                selector=self.graph_loader.get_node_css_selector_repr(item_nodes[0], False, True),
                type='css',
            )

            # items node full extract rule (css)
            full_items_selector = Selector(
                name='items',
                selector=f'{list_selector.selector} > {items_selector.selector}',
                type='css',
            )

            # fields node extract rule
            fields_selectors = self._extract_fields_by_id(list_id=list_node.id, item_nodes=item_nodes)

            # data
            data = self._extract_data(soup, full_items_selector.selector, fields_selectors)

            # result
            result = ListResult(
                selectors={
                    'list': list_selector,
                    'items': items_selector,
                    'full_items': full_items_selector,
                },
                score=score,
                scores=scores,
                fields=fields_selectors,
                data=data,
                detector=DETECTOR_PLAIN_LIST,
            )
            results.append(result)

        return results

    def _sort(self, results: List[ListResult]) -> List[ListResult]:
        results = sorted(results, key=lambda x: x.score, reverse=True)

        # assign name
        for i, result in enumerate(results):
            results[i].name = f'{self.result_name_prefix} {i + 1}'

        return results

    def run(self):
        tic = time.time()

        # train clustering model
        self._train()

        # pre-filter nodes
        res = self._pre_filter()

        # filter nodes
        res = self._filter(*res)

        # extract fields into results
        results = self._extract(*res)

        # sort results
        self.results = self._sort(results)

        toc = time.time()
        logger.debug(f'PlainListExtractor: {toc - tic:.2f}s')

        return self.results


def run_plain_list_detector(url: str, method: str = None) -> PlainListDetector:
    html_requester = HtmlRequester(url=url, request_method=method)
    html_requester.run()

    graph_loader = GraphLoader(html=html_requester.html_, json_data=html_requester.json_data)
    graph_loader.run()

    plain_list_detector = PlainListDetector(html_requester=html_requester, graph_loader=graph_loader)
    plain_list_detector.run()

    return plain_list_detector


if __name__ == '__main__':
    urls = [
        'https://cuiqingcai.com'
    ]
    for url in urls:
        run_plain_list_detector(url)
