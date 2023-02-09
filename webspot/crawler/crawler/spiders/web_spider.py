import json
import os.path

import html_to_json_enhanced
import scrapy
from scrapy.crawler import logger
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor


class WebSpider(scrapy.Spider):
    name = 'web'

    allowed_domains = []

    link_extractor = None

    @property
    def domain(self) -> str:
        return self.settings.get('domain')

    @property
    def urls(self) -> list:
        return self.settings.get('urls') or []

    @property
    def url_paths(self) -> list:
        return self.settings.get('urls_paths') or []

    @property
    def data_root_dir(self) -> str:
        return self.settings.get('data_root_dir') or os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')

    @property
    def data_dir(self) -> str:
        return os.path.join(self.data_root_dir, self.domain)

    @property
    def data_html_dir(self) -> str:
        return os.path.join(self.data_dir, 'html')

    @property
    def data_json_dir(self) -> str:
        return os.path.join(self.data_dir, 'json')

    @property
    def is_test(self) -> bool:
        return self.settings.get('is_test') or False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start_requests(self):
        # log settings
        logger.info(f'settings.domain: {self.domain}')
        logger.info(f'settings.urls: {self.urls}')
        logger.info(f'settings.url_paths: {self.url_paths}')

        # set allowed domains
        self.allowed_domains = [self.domain]

        # link extractor
        self.link_extractor = LxmlLinkExtractor(
            allow=self.url_paths,
            allow_domains=self.allowed_domains,
        )

        for url in self.urls:
            if self.is_test and 'example' in url:
                continue

            yield scrapy.Request(url=url)

    def parse(self, response: scrapy.http.Response, **kwargs):
        # create data html directory if not exists
        if not os.path.exists(self.data_html_dir):
            os.makedirs(self.data_html_dir)

        # create data json directory if not exists
        if not os.path.exists(self.data_json_dir):
            os.makedirs(self.data_json_dir)

        # file name prefix
        filename_prefix = response.url.replace('/', '_').replace(':', '_').replace('.', '_')

        # save response html
        filename = os.path.join(self.data_html_dir, f'{filename_prefix}.html')
        with open(filename, 'wb') as f:
            f.write(response.body)

        # save response json
        filename = os.path.join(self.data_json_dir, f'{filename_prefix}.json')
        with open(filename, 'w') as f:
            json_data = html_to_json_enhanced.convert(response.body, with_id=True)
            f.write(json.dumps(json_data, indent=2))

        # follow links
        for link in self.link_extractor.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse)
