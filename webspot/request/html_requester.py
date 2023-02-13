import json
import os
from urllib.parse import urlparse

import requests

from webspot.request.get_html import get_html

DEFAULT_REQUEST_ROD_URL = 'http://localhost:7777/request'
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))


class HtmlRequester(object):
    def __init__(
        self,
        url: str = None,
        html_path: str = None,
        request_method: str = 'request',
        request_rod_url: str = 'http://localhost:7777/request',
        request_rod_duration: int = 3,
    ):
        # settings
        self.url = url
        self.html_path = html_path
        self.request_method = request_method
        self.request_rod_url = request_rod_url
        self.request_rod_duration = request_rod_duration

    def get_html(self, url: str, request_method: str, request_rod_url: str = DEFAULT_REQUEST_ROD_URL,
                 request_rod_duration: int = 1, save: bool = False) -> str:
        if request_method == 'rod':
            res = requests.post(
                request_rod_url,
                data=json.dumps({'url': url, 'duration': request_rod_duration}),
                headers={'Content-Type': 'application/json'},
            )
            _html = json.loads(res.content.decode('utf-8')).get('html')
        elif request_method == 'request':
            res = requests.get(url)
            _html = res.content.decode('utf-8')
        else:
            raise Exception(f'Invalid request method: {request_method}')

        if save:
            # domain
            domain = urlparse(url).netloc

            # create data html directory if not exists
            data_html_dir = os.path.join(DEFAULT_DATA_DIR, domain, 'html')
            if not os.path.exists(data_html_dir):
                os.makedirs(data_html_dir)

            # create data json directory if not exists
            data_json_dir = os.path.join(DEFAULT_DATA_DIR, domain, 'json')
            if not os.path.exists(data_json_dir):
                os.makedirs(data_json_dir)

            # file name prefix
            filename_prefix = url.replace('/', '_').replace(':', '_').replace('.', '_')

            # save response html
            data_html_dir = os.path.join(DEFAULT_DATA_DIR, domain, 'html')
            filename = os.path.join(data_html_dir, f'{filename_prefix}.html')
            with open(filename, 'w') as f:
                f.write(_html)

            # save response json
            filename = os.path.join(data_json_dir, f'{filename_prefix}.json')
            with open(filename, 'w') as f:
                json_data = html_to_json_enhanced.convert(_html, with_id=True)
                f.write(json.dumps(json_data))

        return _html

    def _request(self):
        self._html = get_html(
            url=self.url,
            request_method=self.request_method,
            request_rod_url=self.request_rod_url,
            request_rod_duration=self.request_rod_duration,
        )

    def run(self):
        # request html page if url exists
        if self.url:
            self._request()
        else:
            with open(self.html_path, 'r') as f:
                self._html = f.read()
