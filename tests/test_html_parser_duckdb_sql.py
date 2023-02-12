import logging
import os
import sqlite3
from unittest import TestCase

import duckdb
import pandas as pd
from parsel import Selector

import tests
from scraperx.utils.config import set_config_level_fmt
from scraperx.utils.misc import get_project_path
from scraperx.utils.parser_ml import train

logger = logging.getLogger("parser.duckdb")


def css(html: str, base_url, value: str):
    sel = Selector(text=html, base_url=base_url)
    return sel.css(value).extract_first()


def xpath(html: str, base_url, value: str):
    sel = Selector(text=html, base_url=base_url)
    return sel.xpath(value).extract()


def json_path(d: dict, path: str):
    pass


class TestDuckdbParserSql(TestCase):

    def setUp(self) -> None:
        set_config_level_fmt()
        self.db = duckdb.connect(database=':memory:')
        self.url = "https://www.google.com"
        self.path = path = "resource/google-search.html"
        self.base_dir = os.path.dirname(tests.__file__)
        with open(os.path.join(self.base_dir, path)) as fp:
            self.nodes = train.parse_as_nodes(fp.read(), self.url, css="*[class]")
            df = pd.DataFrame([x.dict() for x in self.nodes])
            df['base_url'] = self.url
            self.db.register("response", df)
        for item in self.db.query("select * from duckdb_extensions()").fetchall():
            logger.info(item)

    def tearDown(self) -> None:
        self.db.close()

    def test_duckdb_from_html(self):
        sql = "select class_name, text from response where class_name = 'MjjYud'"
        result = self.db.query(sql).fetchall()
        for item in result:
            logger.info(item)


class TestSqliteParserSql(TestCase):

    def setUp(self) -> None:
        set_config_level_fmt()
        self.conn = sqlite3.connect(':memory:')
        self._register_udf()
        self.url = "https://www.google.com"
        self.path = "resource/google-search.html"
        self.base_dir = os.path.dirname(tests.__file__)
        with open(os.path.join(self.base_dir, self.path)) as fp:
            self.nodes = train.parse_as_nodes(fp.read(), self.url, css="*[class]")
            df = pd.DataFrame([x.dict() for x in self.nodes])
            df['base_url'] = self.url
            df.to_sql("response", con=self.conn)
        self._register_udf()

    def _register_udf(self):
        self.conn.create_function("css", 3, css)
        self.conn.create_function("xpath", 3, xpath)
        self.conn.create_function("jmespath", 2, json_path)

    def tearDown(self) -> None:
        self.conn.close()

    def test_sqlite_from_html(self):
        # self.db.arrow()
        sql = "select text, css(html, base_url, 'a::attr(href)') as links from response where class_name = 'MjjYud'"
        result = pd.read_sql(sql, con=self.conn).to_dict("records")
        for item in result:
            logger.info(item)


class TestSqliteHtmlExtension(TestCase):

    def setUp(self) -> None:
        set_config_level_fmt()
        self.conn = sqlite3.connect(':memory:')
        self.conn.enable_load_extension(True)
        self.conn.load_extension(os.path.join(get_project_path(), "extensions/sqlite3/html0"))
        self.conn.load_extension(os.path.join(get_project_path(), "extensions/sqlite3/fileio"))
        self.url = "https://www.google.com"
        self.path = "resource/google-search.html"
        self.base_dir = os.path.dirname(tests.__file__)
        self.index_file = os.path.join(self.base_dir, self.path)


    def tearDown(self) -> None:
        self.conn.close()

    def test_sqlite_from_html(self):
        print(self.conn.execute("select html_version()").fetchone())
        # self.db.arrow()
        sql = """
        select * from html_each(fileio_read('{}'), '.MjjYud')
        """.format(self.index_file)
        result = pd.read_sql(sql, con=self.conn).to_dict("records")
        for item in result:
            logger.info(item)
