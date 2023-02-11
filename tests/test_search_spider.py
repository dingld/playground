import os
from unittest import TestCase
import tests
from scraperx.service import parser

from scrapy import Spider
from scrapy.crawler import CrawlerProcess
from scrapy.http import TextResponse
from twisted.internet.asyncioreactor import install


install()


class Search(Spider):
    name = "search"

    def parse(self, response: TextResponse, **kwargs):
        return parser.parse_index(response.text, response.url)


class TestHtmlClustering(TestCase):

    def setUp(self) -> None:
        self.base_dir = os.path.dirname(tests.__file__)
        self.crawler_process = CrawlerProcess()

    def tearDown(self) -> None:
        self.crawler_process.start()

    def test_google_search(self):
        url = "https://www.google.com.hk/search?q=hello"
        self.crawler_process.crawl(Search, start_urls=[url])

    def test_baidu_search(self):
        url = "http://www.baidu.com/s?wd=hello"
        self.crawler_process.crawl(Search, start_urls=[url])

    def test_bing_search(self):
        url = "https://cn.bing.com/search?q=hello"
        self.crawler_process.crawl(Search, start_urls=[url])

    def test_sougou_search(self):
        url = "https://www.sogou.com/web?query=hello"
        self.crawler_process.crawl(Search, start_urls=[url])

    def test_hdatmos_search(self):
        import scraperx
        path = os.path.join(os.path.dirname(scraperx.__file__), "resource/hdatoms-search.html")
        s = {
            "SPIDER_MIDDLEWARES": {
                "scrapy.spidermiddlewares.depth.DepthMiddleware": None,
                'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': None,
                'scrapy.spidermiddlewares.referer.RefererMiddleware': None,
                'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': None,
            }
        }
        self.crawler_process.settings.update(s)
        self.crawler_process.crawl(Search, start_urls=["file://%s" % path])
