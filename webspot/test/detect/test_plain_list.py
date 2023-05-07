import pytest

from webspot.detect.detectors.plain_list import run_plain_list_detector
from webspot.logging import get_logger

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
        },
    },
    {
        'url': 'https://github.com/trending',
        'result': {
            'selectors': {
                'list': 'main > div.position-relative.container-lg.p-responsive.pt-6 > div.Box > div:last-child'
            }
        },
    },
    {
        'url': 'https://github.com/search?q=spider&type=repositories',
        'result': {
            'selectors': {
                'list': 'div.px-2 > ul.repo-list'
            }
        },
        'index': 1,
    },
    {
        'url': 'http://bang.dangdang.com/books/newhotsales',
        'result': {
            'selectors': {
                'list': 'div.bang_list_box > ul.bang_list.clearfix.bang_list_mode'
            }
        }
    },
    {
        'url': 'https://cuiqingcai.com/archives/',
        'result': {
            'selectors': {
                'list': 'div.post-block > div.posts-collapse'
            }
        }
    },
    {
        'url': 'https://github.com/crawlab-team/crawlab/actions',
        'result': {
            'selectors': {
                'list': '#partial-actions-workflow-runs'
            }
        }
    },
    {
        'url': 'https://huggingface.co/datasets',
        'result': {
            'selectors': {
                'list': 'div.grid.grid-cols-1.gap-5'
            }
        }
    },
    {
        'url': 'https://www.36kr.com/information/web_news/latest/',
        'result': {
            'selectors': {
                'list': 'div.kr-loading-more > div.information-flow-list'
            }
        }
    },
    # {
    #     'url': 'https://cuiqingcai.com',
    #     'result': {
    #         'selectors': {
    #             'list': '.content-wrap > div.content.index.posts-expand'
    #         }
    #     }
    # },
]


# test_cases = [test_cases[-1]]


@pytest.mark.parametrize('test_case', test_cases)
def test_plain_list(test_case):
    url = test_case.get('url')
    method = test_case.get('method') or 'request'
    target_index = test_case.get('target_index') or 0

    logger.info(f'url: {url}')
    logger.info(f'method: {method}')

    plain_list_detector = run_plain_list_detector(url, method)

    results = plain_list_detector.results
    assert len(results) > 0, 'results should be more than 0'

    test_case_result = test_case.get('result')
    test_case_list_selector = test_case_result.get('selectors').get('list')
    target_result = results[target_index]
    assert test_case_list_selector in target_result.selectors.get('list').selector, 'selectors should be matched'
    assert len(target_result.fields) > 0, 'target fields should be more than 0'
    assert len(target_result.data) > 0, 'target data should be more than 0'
