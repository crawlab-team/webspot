import json
import os
from typing import Union
from urllib.parse import urlparse

import html_to_json_enhanced
import requests

from webspot.detect.utils.transform_html_links import transform_html_links

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

        # data
        self.html_: Union[str, None] = None
        self.json_data: Union[dict, None] = None

    @staticmethod
    def _get_html(url: str, request_method: str, request_rod_url: str = DEFAULT_REQUEST_ROD_URL,
                  request_rod_duration: int = 1, save: bool = False):
        if request_method == 'rod':
            # request rod (headless browser)
            res = requests.post(
                request_rod_url,
                data=json.dumps({'url': url, 'duration': request_rod_duration}),
                headers={'Content-Type': 'application/json'},
            )
            html = json.loads(res.content.decode('utf-8')).get('html')
        elif request_method == 'request':
            # plain request
            res = requests.get(url)
            html = res.content.decode('utf-8')
        else:
            raise Exception(f'Invalid request method: {request_method}')

        # convert html to json data
        json_data = html_to_json_enhanced.convert(html, with_id=True)

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
                f.write(html)

            # save response json
            filename = os.path.join(data_json_dir, f'{filename_prefix}.json')
            with open(filename, 'w') as f:
                f.write(json.dumps(json_data))

        return html, json_data

    def _request_html(self):
        self.html_, self.json_data = self._get_html(
            url=self.url,
            request_method=self.request_method,
            request_rod_url=self.request_rod_url,
            request_rod_duration=self.request_rod_duration,
        )

    def _load_html(self):
        with open(self.html_path, 'r') as f:
            self.html_ = f.read()

    def run(self):
        # request html page if url exists
        if self.url:
            self._request_html()
        else:
            self._load_html()

    @property
    def html(self):
        return transform_html_links(self.html_, self.url)
