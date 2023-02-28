import logging
import os.path
from typing import List

from bs4 import BeautifulSoup, Tag

from webspot.detect.models.list_result import ListResult


def get_embed_css() -> str:
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../web/static/css/highlight.css'))
    with open(file_path, 'r') as f:
        return f.read()


def highlight_html(html, results: List[ListResult]) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    for i, result in enumerate(results):
        # list
        list_rule = result.extract_rules.get('list')
        list_el = soup.select_one(list_rule)
        if not list_el:
            continue
        _add_class(list_el, ['webspot-highlight-container', 'webspot-highlight-list-node'])
        _add_label(list_el, soup, f'List {i + 1}', 'primary')

        # items
        items_rule = result.extract_rules.get('items')
        item_els = list_el.select(items_rule)
        for j, item_el in enumerate(item_els):
            _add_class(item_el, ['webspot-highlight-container', 'webspot-highlight-item-node'])
            # _add_label(item_el, soup, f'Item {j + 1}', 'warning')

            # fields
            for k, field in enumerate(result.extract_rules.get('fields')):
                try:
                    field_els = item_el.select(field.get('selector'))
                except Exception as e:
                    # logging.warning(e)
                    field_els = []
                for field_el in field_els:
                    _add_class(field_el, ['webspot-highlight-container', 'webspot-highlight-item-field-node'])
                    # _add_label(field_el, soup, f'Field {k + 1}', 'success')

    # add embed css
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
