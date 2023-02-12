import json
import os
from urllib.parse import urlparse

import html_to_json_enhanced
import requests

DEFAULT_REQUEST_ROD_URL = 'http://localhost:7777/request'
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))


def get_html(url: str, request_method: str, request_rod_url: str = DEFAULT_REQUEST_ROD_URL, save: bool = False) -> str:
    if request_method == 'rod':
        res = requests.post(
            request_rod_url,
            data=json.dumps({'url': url}),
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
