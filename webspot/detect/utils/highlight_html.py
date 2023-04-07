import logging
import os.path
from typing import List

from bs4 import BeautifulSoup, Tag


def get_embed_highlight_css() -> str:
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../web/static/css/embed/highlight.css'))
    with open(file_path, 'r') as f:
        return f.read()


def get_embed_annotate_css() -> str:
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../web/static/css/embed/annotate.css'))
    with open(file_path, 'r') as f:
        return f.read()


def get_embed_annotate_js() -> str:
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../web/static/js/embed/annotate.js'))
    with open(file_path, 'r') as f:
        return f.read()


def embed_highlight(html: str) -> str:
    # soup
    soup = BeautifulSoup(html, 'html.parser')

    # css
    style_el = soup.new_tag('style')
    style_el.append(get_embed_highlight_css())
    soup.select_one('head').append(style_el)

    # html
    return str(soup)


def embed_annotate(html: str) -> str:
    # soup
    soup = BeautifulSoup(html, 'html.parser')

    # css
    style_el = soup.new_tag('style')
    style_el.append(get_embed_annotate_css())
    soup.select_one('head').append(style_el)

    # js
    script_el = soup.new_tag('script')
    script_el.append(get_embed_annotate_js())
    body_el = soup.select_one('body')
    body_el.append(script_el)

    # links
    for a_el in soup.select('a'):
        a_el.attrs['href'] = 'javascript:'

    # html
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
