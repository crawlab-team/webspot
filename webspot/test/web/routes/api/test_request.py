import unittest

import requests


class TestWebRoutesApi(unittest.TestCase):
    def test_post(self):
        res = requests.post('http://localhost:80/api/requests',
                            json={'url': 'https://quotes.toscrape.com', 'method': 'request'})
        assert res.status_code == 200
        data = res.json()
        print(data)
        assert data is not None
        assert data.get('_id') is not None
        assert data.get('url') == 'https://quotes.toscrape.com'


if __name__ == '__main__':
    unittest.main()
