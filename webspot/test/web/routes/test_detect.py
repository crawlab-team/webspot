import unittest

import requests


class TestWebRoutesDetect(unittest.TestCase):
    def test_detect(self):
        res = requests.post('http://localhost:80/api/detect', json={'url': 'https://quotes.toscrape.com'})
        assert res.status_code == 200
        data = res.json()
        assert data is not None
        assert data.get('url') == 'https://quotes.toscrape.com'
        assert data.get('html') is not None and len(data.get('html')) > 0
        assert data.get('results') is not None and len(data.get('results')) > 0

    def test_detect_error(self):
        res = requests.post('http://localhost:80/api/detect',
                            json={'url': 'https://quotes.toscrape.com', 'method': 'xxx'})
        assert res.status_code == 200
        data = res.json()
        assert data is not None
        assert data.get('url') == 'https://quotes.toscrape.com'
        assert data.get('error') is not None


if __name__ == '__main__':
    unittest.main()
