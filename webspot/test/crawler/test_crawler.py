import unittest
from io import StringIO
from unittest.mock import patch

from scrapy.crawler import CrawlerProcess

from webspot.crawler.actions.run_crawler import run_crawler
from webspot.crawler.crawler import WebSpider


class TestCrawler(unittest.TestCase):
    @patch('sys.stderr', new_callable=StringIO)
    def test_settings(self, stderr):
        domain = 'example.com'
        urls = ['https://example.com']
        process = CrawlerProcess(settings={
            'domain': domain,
            'urls': urls,
            'is_test': True,
        })
        process.crawl(WebSpider)
        process.start()
        self.assertTrue(domain in stderr.getvalue())
        self.assertTrue(urls[0] in stderr.getvalue())

    def test_crawl(self):
        domain = 'quotes.toscrape.com'
        urls = ['https://quotes.toscrape.com/']
        run_crawler(domain, urls, is_test=True)


if __name__ == '__main__':
    unittest.main()
