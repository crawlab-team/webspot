from typing import List

from scrapy.crawler import CrawlerProcess

from webspot.crawler.crawler.spiders.web_spider import WebSpider


def run_crawler(domain: str, urls: List[str], url_paths: List[str] = None, data_root_dir: str = None, **kwargs):
    process = CrawlerProcess(settings={
        'domain': domain,
        'urls': urls,
        'url_paths': url_paths,
        'data_root_dir': data_root_dir,
        **kwargs,
    })
    process.crawl(WebSpider)
    process.start()


if __name__ == '__main__':
    run_crawler('https://www.google.com')
