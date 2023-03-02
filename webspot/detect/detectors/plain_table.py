from bs4 import BeautifulSoup

from webspot.detect.detectors.base import BaseDetector


class PlainTableDetector(BaseDetector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def highlight_html(self, html: str, **kwargs) -> str:
        pass

    def _train(self):
        soup = BeautifulSoup(self.html_requester.html, 'html.parser')
        pass

    def run(self):
        pass
