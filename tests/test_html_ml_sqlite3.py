import logging
import os
from unittest import TestCase
from typing import Dict
import tests
from scraperx.utils.config import set_config_level_fmt
from scraperx.utils.parser_sqlite3 import init_sqlite3_conn, init_sqlite3_source, query_sqlite3_as_df
from scraperx.utils.parser_ml import train


logger = logging.getLogger("html.ml.sqlite3")


class TestMLSqliteExtension(TestCase):

    def setUp(self) -> None:
        set_config_level_fmt()
        self.conn = init_sqlite3_conn()
        self.base_dir = os.path.dirname(tests.__file__)
        self.cluster = None
        self.nodes = []

    def _init_with_html(self, path: str, url: str):
        with open(os.path.join(self.base_dir, path)) as fp:
            init_sqlite3_source(conn=self.conn, source=fp.read(), base_url=url)

    def tearDown(self) -> None:
        if not self.cluster:
            return
        group: Dict[int, list] = {}
        for index, label in enumerate(self.cluster.labels_):
            if label == -1:
                logger.info("skip %s", self.nodes[index])
                continue
            group.setdefault(label, []).append(index)
        for label, items in group.items():
            logger.info("starting label %d %s", label, "***" * 30)
            for index in items:
                logger.info("label %d, index=%s, %s", label, index, self.nodes[index])

    def test_extract_feature(self):
        base_url = "https://cn.bing.com"
        self._init_with_html("../configs/source/bing-search.html", base_url)
        sql = """
        WITH A AS (SELECT node.rowid, tag, class, depth, css, xpath

                        FROM response, html_each(response.source, '*[class]') AS node)
        SELECT * FROM A
        """.format(base_url)
        df = query_sqlite3_as_df(self.conn, sql)
        for item in df.to_dict("records"):
            logger.info(item)
        return df

    def test_group_by_class(self):
        base_url = "https://cn.bing.com"
        self._init_with_html("../configs/source/bing-search.html", base_url)
        sql = """
        WITH A AS (SELECT node.rowid, tag, class, depth, css, xpath

                        FROM response, html_each(response.source, '*[class]') AS node 
                    WHERE class IS NOT NULL)
        SELECT depth, class, count() as cnt FROM A group by class, depth having cnt > 3 order by cnt desc
        """.format(base_url)
        df = query_sqlite3_as_df(self.conn, sql)
        for item in df.to_dict("records"):
            logger.info(item)
        return df


    def test_ml_sqlit3_feature(self):
        self.conn.create_aggregate()
        df = self.test_extract_feature()
        feature = df[
            "tag,class,depth,css,xpath".split(",")
        ]
        self.nodes = feature.to_dict("records")
        vectors = train.array_as_onehot_sparse(feature)
        self.cluster = train.do_dbscan(vectors, eps=0.3, min_samples=3)
