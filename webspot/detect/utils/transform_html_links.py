import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag


def transform_html_links(html: str, url: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for el in soup.select('a'):
        _transform_a(el, url)

    for el in soup.select('img'):
        _transform(el, 'src', url)

    for el in soup.select('link'):
        _transform(el, 'href', url)

    for el in soup.select('script'):
        if _is_valid_asset_url(el.get('src')):
            _transform(el, 'src', url)
        else:
            el.decompose()

    return str(soup)


def _transform(el: Tag, key: str, root_url: str):
    if el.get(key) and _is_relative_url_path(el[key]):
        el[key] = transform_url(root_url, el[key])


def _transform_a(el: Tag, root_url: str, target_blank: bool = True):
    key = 'href'
    if el.get(key) and _is_relative_url_path(el[key]):
        url = transform_url(root_url, el[key])
        el[key] = f'/?url={url}'
        if target_blank:
            el['target'] = '_blank'


def _is_valid_asset_url(url: str) -> bool:
    if url is None:
        return False
    for keyword in ['bootstrap', 'jquery']:
        if keyword in url.lower():
            return True
    return False


def _is_relative_url_path(url: str) -> bool:
    return not re.search(re.escape(url), r'^(https?:)?//')


def transform_url(root_url: str, url: str) -> str:
    if not _is_relative_url_path(url):
        return url
    return urljoin(root_url, url)
