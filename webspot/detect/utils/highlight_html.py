import logging
import os.path
from typing import List

from bs4 import BeautifulSoup, Tag

from webspot.detect.models.list_result import ListResult


def get_embed_css() -> str:
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../web/static/css/highlight.css'))
    with open(file_path, 'r') as f:
        return f.read()


def embed_highlight_css(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    style_el = soup.new_tag('style')
    style_el.append(get_embed_css())
    soup.select_one('head').append(style_el)
    return str(soup)


def _add_class(el: Tag, classes: List[str]):
    if not el:
        return
    el_class = el.get('class') or ''
    if isinstance(el_class, str):
        el['class'] = ' '.join([el_class, *classes])
    elif isinstance(el_class, list):
        el['class'] = ' '.join([*el_class, *classes])


def _add_label(el: Tag, soup: BeautifulSoup, label: str, type_: str = None):
    label_el = soup.new_tag('div')
    label_el.append(label)
    el.append(label_el)
    _add_class(label_el, ['webspot-highlight-label'])
    if type_:
        _add_class(label_el, [f'webspot-highlight-label-{type_}'])


def add_class(el: Tag, classes: List[str]):
    return _add_class(el, classes)


def add_label(el: Tag, soup: BeautifulSoup, label: str, type_: str = None):
    return _add_label(el, soup, label, type_)
