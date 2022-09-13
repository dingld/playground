import logging
from unittest import TestCase

import networkx as nx
from matplotlib import pyplot as plt

from brainstorming.search.parser import html
import tests
import os

logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)


class TestHtmlClustering(TestCase):

    def setUp(self) -> None:
        self.base_dir = os.path.dirname(tests.__file__)

    def test_google_search_html_parser(self):

        url = "https://www.google.com"
        path = "resource/google-search.html"
        with open(os.path.join(self.base_dir, path)) as fp:
            nodes = html.parse_as_nodes(fp.read(), url)
        cluster = html.do_dbscan(html.nodes_as_array(nodes), eps=0.2)
        group = {}
        for index, label in enumerate(cluster.labels_):
            if label == -1:
                continue
            group.setdefault(label, []).append(nodes[index])
        g = html.build_graph(group)
        nx.draw(g, with_labels=True)
        plt.show()

    def test_baidu_search_html_parser(self):

        url = "https://www.baidu.com"
        path = "resource/baidu-search.html"
        with open(os.path.join(self.base_dir, path)) as fp:
            nodes = html.parse_as_nodes(fp.read(), url)
        cluster = html.do_dbscan(html.nodes_as_array(nodes), eps=0.2)
        group = {}
        for index, label in enumerate(cluster.labels_):
            if label == -1:
                continue
            group.setdefault(label, []).append(nodes[index])
        g = html.build_graph(group)
        nx.draw(g, with_labels=True)
        plt.show()

    def test_bing_search_html_parser(self):

        url = "https://www.bing.com"
        path = "resource/bing-search.html"
        with open(os.path.join(self.base_dir, path)) as fp:
            nodes = html.parse_as_nodes(fp.read(), url)
        cluster = html.do_dbscan(html.nodes_as_array(nodes), eps=0.2)
        group = {}
        for index, label in enumerate(cluster.labels_):
            if label == -1:
                continue
            group.setdefault(label, []).append(nodes[index])
        g = html.build_graph(group)
        nx.draw(g, with_labels=True)
        plt.show()
