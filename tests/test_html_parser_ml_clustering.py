import logging
import os
from typing import List, Dict
from unittest import TestCase

import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms.tree import recognition
from networkx.drawing import nx_pydot
from networkx.relabel import relabel_nodes

import tests
from scraperx.utils.parser_ml import train
from scraperx.utils.parser_ml.feature import (HtmlNode)

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
        self._draw_cluster_graph()
        self._draw_node_graph()

    def _draw_cluster_graph(self, ):
        group: Dict[int, List[HtmlNode]] = {}
        for index, label in enumerate(self.cluster.labels_):
            if label == -1:
                continue
            group.setdefault(label, []).append(self.nodes[index])
        ctx = dict()
        g = train.build_cluster_graph(group, ctx)
        logging.info("graph count: %d " + "***" * 30, len(g))
        for label, nodes in group.items():
            logging.info("label=%d " + "***" * 30, label, )
            for node in nodes:
                logging.info("node=%s, text: %s", node, node.sel.xpath("string()").extract())
        g = relabel_nodes(g, mapping=ctx)

        nx.draw(g, nx_pydot.graphviz_layout(g, "dot"), with_labels=True)

        plt.show()

        logging.info("is forest %s", recognition.is_forest(g))
        logging.info("is tree %s", recognition.is_tree(g))
        logging.info("root node->%s", ctx)

    def _draw_node_graph(self):
        group: Dict[int, List[HtmlNode]] = {}
        for index, label in enumerate(self.cluster.labels_):
            if label == -1:
                continue
            group.setdefault(label, []).append(self.nodes[index])
        ctx = dict()
        g = train.build_node_graph(group, ctx)
        logging.info("graph count: %d " + "***" * 30, len(g))
        for label, nodes in group.items():
            logging.info("label=%d " + "***" * 30, label, )
            for node in nodes:
                logging.info("node=%s, text: %s", node, node.sel.xpath("string()").extract())
        g = relabel_nodes(g, mapping=ctx)

        nx.draw(g, nx_pydot.graphviz_layout(g, "dot"), with_labels=True)

        plt.show()

        logging.info("is forest %s", recognition.is_forest(g))
        logging.info("is tree %s", recognition.is_tree(g))
        logging.info("root node->%s", ctx)

    def test_google_search_html_parser(self):

        self.url = url = "https://www.google.com"
        self.path = path = "../configs/source/google-search.html"
        with open(os.path.join(self.base_dir, path)) as fp:
            self.nodes = train.parse_as_nodes(fp.read(), url, css="*[class]")
            self.cluster = train.do_dbscan(train.nodes_as_array(self.nodes), eps=0.2)

    def test_baidu_search_html_parser(self):

        self.url = url = "https://www.baidu.com"
        self.path = path = "../configs/source/baidu-search.html"
        with open(os.path.join(self.base_dir, path)) as fp:
            self.nodes = train.parse_as_nodes(fp.read(), url, css="*[class]")
            self.cluster = train.do_dbscan(train.nodes_as_array(self.nodes), eps=0.2)

    def test_bing_search_html_parser(self):
        self.url = url = "https://www.bing.com"
        self.path = path = "../configs/source/bing-search.html"
        with open(os.path.join(self.base_dir, path)) as fp:
            self.nodes = train.parse_as_nodes(fp.read(), url, css="*[class]")
            self.cluster = train.do_dbscan(train.nodes_as_array(self.nodes), eps=0.2)
