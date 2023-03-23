import itertools
from unittest.mock import patch, MagicMock

import pytest

from webspot.constants.request_status import REQUEST_STATUS_SUCCESS, REQUEST_STATUS_PENDING
from webspot.test.web.routes import client

params_url = [
    'https://quotes.toscrape.com',
    'https://books.toscrape.com',
]
params_method = [
    'request',
    # 'rod',
]
params_no_async = [True, False]


@pytest.mark.parametrize('url, method, no_async', list(itertools.product(params_url, params_method, params_no_async)))
@patch('webspot.models.request.Request')
def test_post(mocked_request_model, url, method, no_async):
    # mock the model
    mock_instance = MagicMock()
    mock_instance.save.return_value = None
    mocked_request_model.return_value = mock_instance

    # post
    res = client.post('/api/requests', json={'url': url, 'method': method, 'no_async': no_async})

    # assert
    assert res.status_code == 200
    data = res.json()
    assert data is not None
    assert data.get('url') == url
    assert data.get('method') == method
    assert data.get('no_async') == no_async
    if no_async:
        assert data.get('status') == REQUEST_STATUS_PENDING
    else:
        assert data.get('status') == REQUEST_STATUS_SUCCESS
