import logging
import os
import unittest
from pprint import pformat
import requests

import tests
from scraperx.utils.config import set_config_level_fmt

logger = logging.getLogger("test.parser")


class HtmlScrapeEndpointTest(unittest.TestCase):

    def setUp(self) -> None:
        self.url = "http://127.0.0.1:9090/api/v1/admin/scrape_endpoint"
        self.base_dir = os.path.dirname(tests.__file__)
        set_config_level_fmt()

    def test_download_and_parse(self):
        from scraperx.utils.parser_sqlite3 import init_sqlite3_conn, init_sqlite3_source, query_sqlite3_parser
        url = "https://www.baidu.com/s?word=深圳"
        resp = requests.get(self.url + "/html?url={}".format(url))
        conn = init_sqlite3_conn()

        sql = """
        WITH A AS (SELECT response.base_url, node.*
                        FROM response, html_each(response.source, '.result.c-container') AS node),
            B AS (SELECT html_text(html, 'h3') as title,
                        html_text(html, '.c-gap-top-small') as text,
                        html_attr_get(html, 'h3 a[href]', 'href') as link
                    FROM A)
        SELECT * FROM B WHERE link is not null
        """
        init_sqlite3_source(conn, source=resp.text, base_url=url)
        items = query_sqlite3_parser(conn, sql=sql)
        logger.info("parse items: %d", len(items))
        for item in items:
            logger.info(item)

    def test_baidu_search_parse(self):
        with open(os.path.join(self.base_dir, "resource/baidu-search.html")) as fp:
            html = fp.read()
        rule = {
            "name": "baidu-search",
            "domain": "www.baidu.com",
            "path": "/s",
            "type": 10,
            "rules": [
                """WITH A AS (SELECT response.base_url, node.*
                                                FROM response, html_each(response.source, '.result.c-container') AS node),
                                    B AS (SELECT html_text(html, 'h3') as title,
                                                html_text(html, '.c-gap-top-small') as text,
                                                html_attr_get(html, 'h3 a[href]', 'href') as link
                                            FROM A)
                                SELECT * FROM B WHERE link is not null
                """
            ],
            "ttl": 60 * 60 * 24,
        }
        data = {
            "html": html,
            "url": "https://www.baidu.com/s?word=深圳",
            "rule": rule
        }
        resp = requests.post(self.url + "/parse", json=data)
        logger.info(pformat(resp.json()['data']))


    def test_baidu_search_parse_ml(self):
        with open(os.path.join(self.base_dir, "resource/baidu-search.html")) as fp:
            html = fp.read()
        data = {
            "html": html,
            "url": "https://www.baidu.com/s?word=深圳",
        }
        resp = requests.post(self.url + "/parse_ml", json=data)
        logger.info(pformat(resp.json()))

    def test_baidu_search_parse_factory(self):
        with open(os.path.join(self.base_dir, "resource/baidu-search.html")) as fp:
            html = fp.read()

        data = {
            "html": html,
            "url": "https://www.baidu.com/s?word=深圳"
        }
        resp = requests.post(self.url + "/parse_factory", json=data)
        logger.info(pformat(resp.json()))
