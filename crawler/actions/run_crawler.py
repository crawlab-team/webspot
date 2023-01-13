from typing import List

from scrapy.crawler import CrawlerProcess

from crawler.crawler.spiders.web_spider import WebSpider


def run_crawler(domain: str, urls: List[str], data_root_dir: str = None, **kwargs):
    process = CrawlerProcess(settings={
        'domain': domain,
        'urls': urls,
        'data_root_dir': data_root_dir,
        **kwargs,
    })
    process.crawl(WebSpider)
    process.start()


if __name__ == '__main__':
    run_crawler('https://www.google.com')
