from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag


def transform_html_links(html: str, url: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for link_el in soup.select('a'):
        _transform_a(link_el, url)

    for link_el in soup.select('img'):
        _transform(link_el, 'src', url)

    for link_el in soup.select('link'):
        _transform(link_el, 'href', url)

    for link_el in soup.select('script'):
        _transform(link_el, 'src', url)

    return str(soup)


def _transform(el: Tag, key: str, root_url: str):
    if el.get(key) and el[key].startswith('/'):
        el[key] = urljoin(root_url, el[key])


def _transform_a(el: Tag, root_url: str, target_blank: bool = True):
    key = 'href'
    if el.get(key) and el[key].startswith('/'):
        url = urljoin(root_url, el[key])
        el[key] = f'/?url={url}'
        if target_blank:
            el['target'] = '_blank'
