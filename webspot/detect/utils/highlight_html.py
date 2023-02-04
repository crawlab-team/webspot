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
    for result in results:
        # list
        list_rule = result.extract_rules.get('list')
        list_el = soup.select_one(list_rule)
        if not list_el:
            continue
        _add_class(list_el, ['webspot-highlight-container', 'webspot-highlight-list-node'])

        # items
        items_rule = result.extract_rules.get('items')
        item_els = list_el.select(items_rule)
        for item_el in item_els:
            _add_class(item_el, ['webspot-highlight-container', 'webspot-highlight-item-node'])

            # fields
            for field in result.extract_rules.get('fields'):
                try:
                    field_els = item_el.select(field.get('extract_rule_css'))
                except Exception as e:
                    logging.warning(e)
                    field_els = []
                for field_el in field_els:
                    _add_class(field_el, ['webspot-highlight-container', 'webspot-highlight-item-field-node'])

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
