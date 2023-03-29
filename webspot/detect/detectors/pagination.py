from typing import Optional

import autopager
import numpy as np
import parsel
from bs4 import BeautifulSoup

from webspot.constants.detector import DETECTOR_PAGINATION
from webspot.detect.detectors.base import BaseDetector
from webspot.detect.models.result import Result
from webspot.detect.models.selector import Selector
from webspot.detect.utils.highlight_html import add_class, add_label
from webspot.detect.utils.transform_html_links import transform_url
from webspot.detect.utils.url import get_url_domain


class PaginationDetector(BaseDetector):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._at_res: list = []
        self._el_next: Optional[parsel.selector.Selector] = None
        self.next_url: Optional[str] = None

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

    def _train(self) -> np.array:
        self._at_res = autopager.extract(self.html_requester.html_)
        _els_next = [t[1] for t in self._at_res if t[0] == 'NEXT']
        if len(_els_next) == 0:
            return
        self._el_next = _els_next[0]
        self.next_url = self._el_next.attrib.get('href')

    def _extract(self):
        if not self.next_url:
            return

        _nodes = [n for n in self.link_nodes if
                  transform_url(self.root_url, n.attrs.get('href')) == transform_url(self.root_url, self.next_url)]
        if len(_nodes) == 0:
            return
        next_node = _nodes[-1]
        next_selector = Selector(
            name='pagination',
            selector=self.graph_loader.get_node_css_selector_path(next_node),
            type='css',
            node_id=next_node.id,
        )
        score = 1.0
        self.results.append(Result(
            name='Next',
            score=score,
            scores={'score': score},
            selectors={
                'next': next_selector,
            },
            detector=DETECTOR_PAGINATION,
        ))

    def run(self):
        self._train()

        self._extract()

        return self.results
