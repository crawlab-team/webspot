from urllib.parse import urlparse

import numpy as np
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

from webspot.constants.detector import DETECTOR_PAGINATION
from webspot.detect.detectors.base import BaseDetector
from webspot.detect.models.result import Result
from webspot.detect.models.selector import Selector
from webspot.detect.utils.highlight_html import add_class, add_label
from webspot.detect.utils.transform_html_links import transform_url
from webspot.detect.utils.url import get_url_domain
from webspot.graph.graph_loader import GraphLoader
from webspot.request.html_requester import HtmlRequester


class PaginationDetector(BaseDetector):
    def __init__(
        self,
        score_threshold: float = 1.,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # settings
        self.keywords = [
            'next',
            '下一页',
        ]
        self.escape_feature_names = [
            'src',
            'href',
        ]
        self.url_sep = '/'
        self.numeric_mask = '#NUMERIC#'
        self.score_threshold = score_threshold

        # vectorizer
        self.vec = TfidfVectorizer()

        # data
        self.internal_link_nodes = None
        self.scores_url_path_fragments = None
        self.scores_feature_next = None
        self.scores_text = None
        self._scores = None
        self._scores_idx = None
        self._scores_idx_max = None

    def highlight_html(self, html: str, **kwargs) -> str:
        soup = BeautifulSoup(html, 'html.parser')

        if len(self.results) == 0:
            return html

        result = self.results[0]
        next_selector = result.selectors.get('next')
        next_el = soup.select_one(next_selector.selector)
        if next_el is None:
            return html

        add_class(next_el, ['webspot-highlight-container', 'webspot-highlight-node-color__red'])
        add_label(next_el, soup, f'Pagination', 'primary')

        return str(soup)

    @property
    def root_url(self):
        return self.html_requester.url

    def _get_masked_fragment(self, fragment: str):
        if fragment.isdigit():
            return self.numeric_mask
        return fragment

    def _get_url_path_fragment(self, url: str):
        return [
            self._get_masked_fragment(f.lower())
            for f in urlparse(url).path.split(self.url_sep)
            if f != ''
        ]

    @property
    def current_url_path_fragments(self):
        return self._get_url_path_fragment(self.root_url)

    @property
    def link_nodes(self):
        return [n for n in self.get_nodes_by_feature(feature_key='tag', feature_value='a')
                if n.attrs.get('href') is not None]

    def _get_internal_link_nodes(self):
        self.internal_link_nodes = [
            n
            for n in self.link_nodes
            if get_url_domain(transform_url(self.root_url, n.attrs.get('href'))) == get_url_domain(self.root_url)
        ]

    @property
    def internal_link_nodes_ids(self):
        return [n.id for n in self.internal_link_nodes]

    @property
    def internal_link_nodes_idx(self):
        nodes_ids = self.graph_loader.nodes_ids_tensor.detach().numpy()
        internal_link_nodes_ids_enc = self.graph_loader.node_ids_enc.transform(self.internal_link_nodes_ids)
        return np.argwhere(np.isin(nodes_ids, internal_link_nodes_ids_enc))

    def _calculate_scores_url_path_fragments(self):
        hrefs = [transform_url(self.root_url, n.attrs.get('href')) for n in self.internal_link_nodes]

        fragments_list = [self._get_url_path_fragment(href) for href in hrefs]

        # join the fragments of list into a single string
        corpus = [' '.join(fragments) for fragments in fragments_list]
        if len(corpus) == 0:
            return

        # fit the vectorizer on the collection
        fragments_list_mat = self.vec.fit_transform(corpus)

        # transform the current url path fragments
        current_fragments_vec = self.vec.transform([' '.join(self.current_url_path_fragments)])

        # calculate the cosine similarity
        self.scores_url_path_fragments = cosine_similarity(fragments_list_mat, current_fragments_vec)

    def _calculate_scores_feature_next(self):
        feature_names = self.graph_loader.nodes_features_enc.feature_names_

        features_hits = np.zeros(len(feature_names))

        for i, f in enumerate(feature_names):
            k = f.split('=')[0]
            if k in self.escape_feature_names:
                continue

            v = '='.join(f.split('=')[1:])
            for keyword in self.keywords:
                if keyword in v.lower():
                    features_hits[i] = 1
                    break

        features_hit_idx = np.argwhere(features_hits == 1).T[0]

        internal_nodes_hit_features = self.graph_loader.nodes_features_tensor[
            self.internal_link_nodes_idx,
            features_hit_idx,
        ].detach().numpy()

        normalized_feat = np.array([internal_nodes_hit_features.sum(axis=1)]).T

        self.scores_feature_next = np.log(normalized_feat + 1)

    def _calculate_scores_text(self):
        texts_hits = np.array([[
            len(set(n.text.lower().split(' ')).intersection(self.keywords)) > 0 if n.text else False
            for n in self.internal_link_nodes
        ]]) * 1
        texts_hits = texts_hits.T
        self.scores_text = np.log(texts_hits + 1)

    def _pre_process(self):
        self._get_internal_link_nodes()

    def _train(self) -> np.array:
        self._calculate_scores_url_path_fragments()
        self._calculate_scores_feature_next()
        self._calculate_scores_text()

        if self.scores_url_path_fragments is None or self.scores_feature_next is None or self.scores_text is None:
            self.scores = np.array([])
            return

        self._scores = normalize(
            np.concatenate(
                (
                    self.scores_url_path_fragments,
                    self.scores_feature_next,
                    self.scores_text,
                ),
                axis=1,
            ),
            norm='l2',
            axis=1,
        )
        self.scores = self._scores.sum(axis=1)

    def _filter(self):
        self._scores_idx = np.argwhere(self.scores >= self.score_threshold).T[0]

    def _sort(self):
        if len(self._scores_idx) == 0:
            return

        _idx = np.argmax(self.scores[self._scores_idx])
        self._scores_idx_max = self._scores_idx[_idx]

    def _extract(self):
        if self._scores_idx_max is None:
            return

        node = self.internal_link_nodes[self._scores_idx_max]
        next_selector = Selector(name='next', selector=self.graph_loader.get_node_css_selector_path(node))
        score = self.scores[self._scores_idx_max]
        score_url_path_fragments = self._scores[self._scores_idx_max][0]
        score_feature_next = self._scores[self._scores_idx_max][1]
        score_text = self._scores[self._scores_idx_max][2]

        self.results.append(Result(
            name='Next',
            score=score,
            scores={
                'url_path_fragments': score_url_path_fragments,
                'feature_next': score_feature_next,
                'text': score_text,
            },
            selectors={
                'next': next_selector,
            },
            detector=DETECTOR_PAGINATION,
        ))

    def run(self):
        self._pre_process()

        self._train()

        self._filter()

        self._sort()

        self._extract()

        return self.results


if __name__ == '__main__':
    urls = [
        # 'https://www.baidu.com/s?wd=crawlab',
        # 'https://github.com/search?q=spider',
        # 'https://www.bing.com/search?q=crawlab&form=QBLHCN&sp=-1&lq=0&pq=&sc=0-0&qs=n&sk=&cvid=BB20795C2CB64FCFBC5A0B69070A11AA&ghsh=0&ghacc=0&ghpl=',
        # 'https://www.bing.com/search?q=crawlab&sp=-1&lq=0&pq=&sc=0-0&qs=n&sk=&cvid=BB20795C2CB64FCFBC5A0B69070A11AA&ghsh=0&ghacc=0&ghpl=&first=11&FORM=PORE',
        # 'https://github.com/trending',
        # 'https://github.com/crawlab-team/crawlab/actions',
        'https://quotes.toscrape.com',
        # 'https://quotes.toscrape.com/page/2/',
        # 'https://books.toscrape.com',
        # 'https://cuiqingcai.com/archives/',
        # 'https://cuiqingcai.com/archives/page/2/',
    ]

    for url in urls:
        html_requester = HtmlRequester(url=url, request_method='request')
        html_requester.run()

        graph_loader = GraphLoader(html=html_requester.html_, json_data=html_requester.json_data)
        graph_loader.run()

        pagination_detector = PaginationDetector(html_requester=html_requester, graph_loader=graph_loader)
        pagination_detector.run()
        print(url)
        print(pagination_detector.results)
        print('\n\n')
