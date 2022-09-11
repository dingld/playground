import logging
from typing import List, Dict

import networkx as nx
import pandas as pd
from lxml import etree
from parsel import Selector
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import OneHotEncoder

from brainstorming.search.parser.unit import (HtmlNode, HtmlNodeGraph)

logger = logging.getLogger("parser.html")


def parse_as_nodes(html: str, url, minimum: int = 5, css: str = "div[class]",
                   with_children: bool = True, with_text: bool = True) -> List[HtmlNode]:
    sel: Selector = Selector(text=html, base_url=url)
    tree = etree.ElementTree(sel.root)
    nodes = list(map(lambda x: HtmlNode.from_element(x.root, tree), sel.css("body %s" % css)))
    filtered_nodes = pre_filter_by_group_size(nodes, minimum)
    if with_children:
        filtered_nodes = list(filter(lambda x: x.children, filtered_nodes))
    if with_text:
        filtered_nodes = list(filter(lambda x: x.html_element.text_content(), filtered_nodes))
    logging.debug("parse filtered nodes=%d/%d, url=%s", len(filtered_nodes), len(nodes), url)
    return filtered_nodes


def nodes_as_array(nodes: List[HtmlNode]):
    rows = list(map(lambda x: x.row(), nodes))
    vectors = OneHotEncoder(sparse=True).fit_transform(pd.DataFrame(rows))
    return vectors


def do_dbscan(vectors, eps: float = 0.5, min_samples: int = 3) -> DBSCAN:
    clustering = DBSCAN(eps=eps, min_samples=min_samples)
    clustering.fit(vectors)
    return clustering


def build_graph(groups: Dict[int, List[HtmlNode]]):
    g = nx.DiGraph()
    color_map = {}
    graphs = []
    for label, members in groups.items():
        color_map[label] = label
        group = HtmlNodeGraph(label, members)
        graphs.append(group)
        logging.debug("graph label=%d, member=%d, xpath=%s", group.label, len(group.members), group.xpath())
        # for m in members:
        #     g.add_edge("%d-%s" % (label, m), label)
    graphs: List[HtmlNodeGraph] = sorted(graphs, key=lambda x: x.depth(), reverse=True)
    for i in range(len(graphs)):
        u: HtmlNodeGraph = graphs[i]
        logging.info("label %s of depth %d ", u.label, u.depth())
        if i == len(graphs) - 1:
            g.add_edge(u.head(), u.label)
            break
        for j in range(i + 1, len(graphs)):
            v: HtmlNodeGraph = graphs[j]
            if u.subgraph_to(v):
                g.add_edge(v.label, u.label)
                logging.info("label %s of depth %d is subgraph to %d depth %d", u.label, u.depth(), v.label, v.depth())
                break
        else:
            g.add_edge(u.head(), u.label)
    return g


def pre_filter_by_group_size(nodes: List[HtmlNode], minimum=3) -> List[HtmlNode]:
    groups = {}
    for node in nodes:
        key = str(node)
        groups[key] = groups.get(key, 0) + 1
    output = []
    for node in nodes:
        key = str(node)
        if groups[key] < minimum:
            continue
        output.append(node)
    return output
