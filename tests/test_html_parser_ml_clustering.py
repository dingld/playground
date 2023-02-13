import logging
import os
from unittest import TestCase
from urllib3.util import parse_url
from typing import List, Dict
import networkx as nx
from matplotlib import pyplot as plt

import tests
from scraperx.utils.parser_ml.feature import (HtmlNode)
from scraperx.utils.parser_ml import train

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)


class TestHtmlClustering(TestCase):

    def setUp(self) -> None:
        self.base_dir = os.path.dirname(tests.__file__)
        self.nodes: List[HtmlNode] = []
        self.cluster = None
        self.path = ""
        self.url = ""
        os.chdir(self.base_dir)

    def tearDown(self) -> None:
        if not self.cluster:
            return
        group: Dict[int, List[HtmlNode]] = {}
        for index, label in enumerate(self.cluster.labels_):
            if label == -1:
                continue
            group.setdefault(label, []).append(self.nodes[index])
        g = train.build_graph(group)
        for label, nodes in group.items():
            logging.info("label=%d " + "***" * 30, label, )
            for node in nodes:
                logging.info("node=%s, text: %s", node, node.sel.xpath("string()").extract())
        nx.draw(g, with_labels=True)
        fname = "%s.jpeg" % parse_url(self.url).host
        plt.savefig(fname)
        os.system("open %s" % fname)

    def test_google_search_html_parser(self):

        self.url = url = "https://www.google.com"
        self.path = path = "resource/google-search.html"
        with open(os.path.join(self.base_dir, path)) as fp:
            self.nodes = train.parse_as_nodes(fp.read(), url)
            self.cluster = train.do_dbscan(train.nodes_as_array(self.nodes), eps=0.2)

    def test_baidu_search_html_parser(self):

        self.url = url = "https://www.baidu.com"
        self.path = path = "resource/baidu-search.html"
        with open(os.path.join(self.base_dir, path)) as fp:
            self.nodes = train.parse_as_nodes(fp.read(), url)
            self.cluster = train.do_dbscan(train.nodes_as_array(self.nodes), eps=0.2)

    def test_bing_search_html_parser(self):

        self.url = url = "https://www.bing.com"
        self.path = path = "resource/bing-search.html"
        with open(os.path.join(self.base_dir, path)) as fp:
            self.nodes = train.parse_as_nodes(fp.read(), url)
            self.cluster = train.do_dbscan(train.nodes_as_array(self.nodes), eps=0.2)
