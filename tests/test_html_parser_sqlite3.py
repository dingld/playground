import logging
import os
from unittest import TestCase

import tests
from scraperx.utils.config import set_config_level_fmt
from scraperx.utils.parser_sqlite3 import init_sqlite3_conn, init_sqlite3_source, query_sqlite3_parser

logger = logging.getLogger("parser.html.sqlite3")


class TestSqliteHtmlExtension(TestCase):

    def setUp(self) -> None:
        set_config_level_fmt()
        self.conn = init_sqlite3_conn()
        self.base_dir = os.path.dirname(tests.__file__)

    def tearDown(self) -> None:
        sql = "select base_url, created_at from response"
        for item in query_sqlite3_parser(self.conn, sql):
            logger.info(item)

    def _init_with_html(self, path: str, url: str):
        with open(os.path.join(self.base_dir, path)) as fp:
            init_sqlite3_source(conn=self.conn, source=fp.read(), base_url=url)

    def test_parse_twice(self):
        self.test_html_parser_sqlite3_baidu()
        self.test_html_parser_sqlite3_baidu()

    def test_html_parser_sqlite3_google(self):
        base_url = "https://www.google.com"
        self._init_with_html("../configs/source/google-search.html", base_url)
        sql = """
        WITH A AS (SELECT response.base_url, node.* 
                    FROM response, html_each(response.source, '.MjjYud, .AaVjTc') AS node),
            B AS (SELECT html_text(html, '.MUxGbd.wuQ4Ob.WZ8Tjf') as date, 
                        html_text(html, 'h3') as title, 
                        text,
                        html_attr_get(html, 'a[class]', 'href') as link
                    FROM A)
        SELECT * FROM B WHERE link is not null
        """.format(base_url)
        for item in query_sqlite3_parser(self.conn, sql):
            logger.info(item)

    def test_html_parser_sqlite3_bing(self):
        base_url = "https://cn.bing.com"
        self._init_with_html("../configs/source/bing-search.html", base_url)
        sql = """
        WITH A AS (SELECT response.base_url, node.* 
                        FROM response, html_each(response.source, '.b_algo,.fl') AS node),
            B AS (SELECT html_text(html, '.b_title') as title, 
                        html_text(html, '.b_caption') as text,
                        html_attr_get(html, 'a[class]', 'href') as link
                    FROM A)
        SELECT * FROM B WHERE link is not null
        """.format(base_url)
        for item in query_sqlite3_parser(self.conn, sql):
            logger.info(item)

    def test_html_parser_sqlite3_baidu(self):
        base_url = "https://www.baidu.com"
        self._init_with_html("../configs/source/baidu-search.html", base_url)
        sql = """
        WITH A AS (SELECT response.base_url, node.* 
                        FROM response, html_each(response.source, '.result.c-container') AS node),
            B AS (SELECT html_text(html, 'h3') as title, 
                        html_text(html, '.c-gap-top-small') as text,
                        html_attr_get(html, 'h3 a[href]', 'href') as link
                    FROM A)
        SELECT * FROM B WHERE link is not null
        """.format(base_url)
        items = query_sqlite3_parser(self.conn, sql)
        logger.info("parse items: %d", len(items))
        for item in items:
            logger.info(item)
