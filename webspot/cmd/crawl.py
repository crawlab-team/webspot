from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pandas import DataFrame

from webspot.constants.detector import DETECTOR_PLAIN_LIST, DETECTOR_PAGINATION
from webspot.extract.extract_results import extract_rules


def cmd_crawl(args):
    url = args.url

    results, execution_time, html_requester, graph_loader, detectors = extract_rules(
        url=url,
    )

    # plain list
    result_plain_list = results.get(DETECTOR_PLAIN_LIST)
    if result_plain_list is None or len(result_plain_list) == 0:
        return

    # items
    full_items = result_plain_list[0].get('selectors').get('full_items')
    items_selector = full_items.get('selector')
    # print(items_selector)

    # fields
    fields = result_plain_list[0].get('fields')
    # print(fields)

    # pagination
    result_pagination = results.get(DETECTOR_PAGINATION)
    pagination_selector = None
    if result_pagination is not None and len(result_pagination) > 0:
        pagination_selector = result_pagination[0].get('selectors').get('next').get('selector')
    # print(pagination_selector)

    res = crawl_page(url, items_selector, fields, pagination_selector)
    print(DataFrame(list(res)))


def crawl_page(url, items_selector, fields, pagination_selector):
    print(f'requesting {url}')
    res = requests.get(url)
    soup = BeautifulSoup(res.content, features='lxml')

    for el_item in soup.select(items_selector):
        row = {}
        for f in fields:
            try:
                if f.get('attribute'):
                    row[f.get('name')] = el_item.select_one(f.get('selector')).attrs.get(f.get('attribute'))
                else:
                    row[f.get('name')] = el_item.select_one(f.get('selector')).text.strip()
            except:
                pass
        yield row

    if pagination_selector is not None:
        try:
            href = soup.select_one(pagination_selector).attrs.get('href')
            next_url = urljoin(url, href)

            for row in crawl_page(next_url, items_selector, fields, pagination_selector):
                yield row
        except:
            pass
