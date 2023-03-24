import json
import logging
import os
from typing import Optional
from urllib.parse import urlparse

import html_to_json_enhanced
import httpx
from httpx import Timeout
from requests import Response
from retrying import retry

from webspot.constants.html_request_method import HTML_REQUEST_METHOD_REQUEST, HTML_REQUEST_METHOD_ROD
from webspot.detect.utils.transform_html_links import transform_html_links

DEFAULT_REQUEST_ROD_URL = 'http://localhost:7777/request'
DEFAULT_REQUEST_ROD_DURATION = 10
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))


class HtmlRequester(object):
    def __init__(
        self,
        url: str = None,
        html_path: str = None,
        request_method: str = HTML_REQUEST_METHOD_REQUEST,
        request_rod_url: str = DEFAULT_REQUEST_ROD_URL,
        request_rod_duration: int = DEFAULT_REQUEST_ROD_DURATION,
        save: bool = False,
    ):
        # settings
        self.url = url
        self.html_path = html_path
        self.request_method = request_method
        self.request_rod_url = request_rod_url
        self.request_rod_duration = request_rod_duration
        self.save = save
        self.encodings = ['utf-8', 'gbk', 'iso-8859-1', 'cp1252']

        # data
        self.html_: Optional[str] = None
        self.html_response: Optional[Response] = None
        self.json_data: Optional[dict] = None

        # logger
        self.logger = logging.getLogger('webspot.request.html_requester')

    def _decode_response_content(self, res: Response) -> str:
        content = ''
        for encoding in self.encodings:
            try:
                content = res.content.decode(encoding)
                break
            except UnicodeDecodeError:
                pass
        return content

    @retry(stop_max_attempt_number=3, wait_fixed=100)
    def _request_html(self):
        url = self.url
        request_method = self.request_method
        request_rod_url = self.request_rod_url
        request_rod_duration = self.request_rod_duration

        # print info
        self.logger.info(f'Requesting {url} [method="{request_method}", duration={self.request_rod_duration}]')

        if request_method == HTML_REQUEST_METHOD_ROD:
            # request rod (headless browser)
            res = httpx.post(
                request_rod_url,
                json={'url': url, 'duration': request_rod_duration},
                headers={'Content-Type': 'application/json'},
            )
            if res.status_code != 200:
                raise Exception(f'Invalid response from request rod: {res.status_code}')
            self.html_response = res
            self.html_ = json.loads(self._decode_response_content(res)).get('html')
        elif request_method == HTML_REQUEST_METHOD_REQUEST:
            # plain request
            res = httpx.get(url, timeout=Timeout(timeout=self.request_rod_duration), follow_redirects=True)
            if res.status_code != 200:
                raise Exception(f'Invalid response from request: {res.status_code}')
            self.html_response = res
            self.html_ = self._decode_response_content(res)
        else:
            raise Exception(f'Invalid request method: {request_method}')

        # convert html to json data
        self.json_data = html_to_json_enhanced.convert(self.html_, with_id=True)

        if self.save:
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
                f.write(self.html_)

            # save response json
            filename = os.path.join(data_json_dir, f'{filename_prefix}.json')
            with open(filename, 'w') as f:
                f.write(json.dumps(self.json_data))

    def _load_html(self):
        # print info
        self.logger.info(f'Loading html from {self.html_path}...')

        with open(self.html_path, 'r') as f:
            self.html_ = f.read()

    def run(self):
        # request html page if url exists
        if self.url:
            self._request_html()
        elif self.html_path:
            self._load_html()
        else:
            raise Exception('No url or html path provided')

        assert self.html_ is not None, 'No html obtained!'

    @property
    def html(self):
        return transform_html_links(self.html_, self.url)
