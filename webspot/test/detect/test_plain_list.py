import itertools
import unittest

import pytest

from webspot.detect.detectors.plain_list import PlainListDetector, run_plain_list_detector
from webspot.graph.graph_loader import GraphLoader
from webspot.logging import get_logger
from webspot.request.html_requester import HtmlRequester

logger = get_logger('webspot.test.detect.test_plain_list')

test_cases = [
    {
        'url': 'https://quotes.toscrape.com',
        'result': {
            'selectors': {
                'list': 'body > div.container > div.row:last-child > div.col-md-8'
            }
        }
    },
    {
        'url': 'https://books.toscrape.com',
        'result': {
            'selectors': {
                'list': 'section > div:last-child > ol.row'
            }
        }
    },
    {
        'url': 'https://github.com/trending',
        'result': {
            'selectors': {
                'list': 'main > div.position-relative.container-lg.p-responsive.pt-6 > div.Box > div:last-child'
            }
        }
    },
    {
        'url': 'https://github.com/search?q=spider',
        'result': {
            'selectors': {
                'list': '.pt-md-0 > div.px-2 > ul.repo-list'
            }
        }
    },
    {
        'url': 'https://cuiqingcai.com',
        'result': {
            'selectors': {
                'list': '.content-wrap > div.content.index.posts-expand'
            }
        }
    },
    {
        'url': 'https://cuiqingcai.com/archives/',
        'result': {
            'selectors': {
                'list': '.post-block > div.posts-collapse'
            }
        }
    },
    # {'url': 'https://github.com/crawlab-team/crawlab/actions'},
    # {'url': 'https://cuiqingcai.com/archives/page/2/'},
    # {
    #     'url': 'https://www.baidu.com/s?wd=crawlab',
    #     'result': {
    #         'selectors': {
    #             'list': '',
    #         }
    #     },
    # },
]
test_cases = [test_cases[-2]]


@pytest.mark.parametrize('test_case', test_cases)
def test_plain_list(test_case):
    url = test_case.get('url')
    logger.info(f'url: {url}')

    plain_list_detector = run_plain_list_detector(url)

    results = plain_list_detector.results
    assert len(results) > 0, 'results should be more than 0'

    test_case_result = test_case.get('result')
    test_case_list_selector = test_case_result.get('selectors').get('list')
    target_result = results[0]
    assert target_result.selectors.get('list').selector == test_case_list_selector, 'selectors should be equal'
    assert len(target_result.fields) > 0, 'target fields should be more than 0'
    assert len(target_result.data) > 0, 'target data should be more than 0'
