import logging
from unittest import TestCase

import networkx as nx
from matplotlib import pyplot as plt

from brainstorming.search.parser import html

logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)


class TestHtmlClustering(TestCase):

    def test_google_search_html_parser(self):

        url = "https://www.google.com"
        with open("resource/google-search.html") as fp:
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
        with open("resource/baidu-search.html") as fp:
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
        with open("resource/bing-search.html") as fp:
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
