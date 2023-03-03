from bs4 import BeautifulSoup
import numpy as np

from webspot.detect.detectors.base import BaseDetector


class PlainTableDetector(BaseDetector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # data
        self._table_nodes = None

    def highlight_html(self, html: str, **kwargs) -> str:
        pass

    @property
    def table_nodes(self):
        return self.get_nodes_by_feature(feature_key='tag', feature_value='table')

    def _pre_process(self):
        self._table_nodes = self.table_nodes

    def _train(self):
        pass

    def run(self):
        self._pre_process()

        self._train()
