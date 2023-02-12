import logging
import os
import sqlite3
from unittest import TestCase

import pandas as pd

import tests
from scraperx.utils.config import set_config_level_fmt
from scraperx.utils.misc import get_project_path

logger = logging.getLogger("parser.html.sqlite3")


class TestSqliteHtmlExtension(TestCase):

    def setUp(self) -> None:
        set_config_level_fmt()
        self.conn = sqlite3.connect(':memory:')
        self.conn.enable_load_extension(True)
        self.conn.load_extension(os.path.join(get_project_path(), "extensions/sqlite3/html0"))
        self.url = "https://www.google.com"
        self.path = "resource/google-search.html"
        self.base_dir = os.path.dirname(tests.__file__)
        self.index_file = os.path.join(self.base_dir, self.path)
        with open(self.index_file) as fp:
            df = pd.DataFrame([{"source": fp.read()}])
            df['base_url'] = self.url
            df.to_sql("response", con=self.conn)

    def tearDown(self) -> None:
        self.conn.close()

    def test_sqlite_from_html(self):
        sql = """
        WITH A AS (SELECT node.* FROM response, html_each(source, 'a[class],b') AS node),
            B AS (SELECT base_url, 
                        html_attr_get(html, 'a[href^="/search"]', 'href') as link, 
                        html_attr_get(html, 'a[href^="/search"]', 'class') as class, 
                        text 
                    FROM A, response)
        SELECT * FROM B WHERE link is not null
        """.format(self.index_file)
        result = pd.read_sql(sql, con=self.conn).to_dict("records")
        for item in result:
            logger.info(item)
