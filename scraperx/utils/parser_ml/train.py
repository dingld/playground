import logging
from typing import List, Dict

import networkx as nx
import pandas as pd
from lxml import etree
from parsel import Selector
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import OneHotEncoder

from scraperx.utils.parser_ml.feature import (HtmlNode, HtmlClusterGraph)

logger = logging.getLogger("parser_ml.html")


def parse_as_nodes(html: str, url, minimum: int = 5, css: str = "*[class]",
                   with_children: bool = True, with_text: bool = True) -> List[HtmlNode]:
    sel: Selector = Selector(text=html, base_url=url)
    tree = etree.ElementTree(sel.root)
    nodes = list(map(lambda x: HtmlNode.from_element(x, tree), sel.css("body %s" % css)))
    filtered_nodes = pre_filter_by_group_size(nodes, minimum)
    if with_children:
        filtered_nodes = list(filter(lambda x: x.children, filtered_nodes))
    if with_text:
        filtered_nodes = list(filter(lambda x: x.html_element.text_content(), filtered_nodes))
    logger.info("parse filtered nodes=%d/%d, url=%s", len(filtered_nodes), len(nodes), url)
    return filtered_nodes


def nodes_as_array(nodes: List[HtmlNode]):
    rows = list(map(lambda x: x.row(), nodes))
    vectors = OneHotEncoder(sparse=True).fit_transform(pd.DataFrame(rows))
    return vectors


def do_dbscan(vectors, eps: float = 0.5, min_samples: int = 3) -> DBSCAN:
    clustering = DBSCAN(eps=eps, min_samples=min_samples)
    clustering.fit(vectors)
    return clustering


def build_cluster_graph(groups: Dict[int, List[HtmlNode]], context: dict):
    g = nx.DiGraph()
    color_map = {}
    graphs = []
    for label, members in groups.items():
        color_map[label] = label
        cluster_group = HtmlClusterGraph(label, members)
        graphs.append(cluster_group)
        logger.debug("graph label=%d, depth=%d, member=%d, head=%-30s, full=%s", cluster_group.label,
                     cluster_group.depth(), len(cluster_group.members),
                     cluster_group.head(), cluster_group.head(True))

    # depth reverse search ancestor
    graphs: List[HtmlClusterGraph] = sorted(graphs, key=lambda x: x.depth(), reverse=True)
    subgraph_set = set()
    for index, current_g in enumerate(graphs):
        current_g: HtmlClusterGraph = current_g
        logger.debug("*****" * 30)
        logger.debug("current graph label=%d, depth=%d, member=%d, head=%-30s, full=%s", current_g.label,
                     current_g.depth(), len(current_g.members), current_g.head(), current_g.head(True))
        if index == len(graphs) - 1:
            break
        for next_g in graphs[index + 1:]:
            if current_g == next_g:
                continue
            next_g: HtmlClusterGraph = next_g
            if current_g.subgraph_to(next_g):
                g.add_edge(next_g.label, current_g.label)
                logging.debug("add edge: %s -> %s,  depth=%d, head=%s", next_g.label, current_g.label, next_g.depth(),
                              next_g.head())
                subgraph_set.add(current_g.label)
                break

    for current_g in graphs:
        if current_g.label in subgraph_set:
            continue
        context[current_g.label] = current_g.head()
        g.add_node(current_g.label)
        context[current_g.label] = current_g.head()
        logging.debug("set as root label=%s, head=%s, depth=%d", current_g.label, current_g.head(),
                      current_g.depth())
    return g


def build_node_graph(groups: Dict[int, List[HtmlNode]], context: dict):
    G = nx.DiGraph()
    color_map = {}
    graphs = []
    for label, members in groups.items():
        color_map[label] = label
        cluster_group = HtmlClusterGraph(label, members)
        graphs.append(cluster_group)

    # depth reverse search ancestor
    graphs: List[HtmlClusterGraph] = sorted(graphs, key=lambda x: x.depth(), reverse=True)
    subnode_set = set()
    for index, current_g in enumerate(graphs):
        current_g: HtmlClusterGraph = current_g
        logger.debug("*****" * 30)
        logger.debug("current graph label=%d, depth=%d, member=%d, head=%-30s, full=%s", current_g.label,
                     current_g.depth(), len(current_g.members), current_g.head(), current_g.head(True))
        if index == len(graphs) - 1:
            break

        for next_g in graphs[index + 1:]:
            if current_g == next_g:
                continue
            next_g: HtmlClusterGraph = next_g
            if current_g.subgraph_to(next_g):
                for current_node_index, current_node in enumerate(current_g.members):
                    for next_node_index, next_node in enumerate(next_g.members):
                        if current_node.has_ancestor(next_node.html_element):
                            u = "%d-%s" % (next_g.label, next_node_index)
                            v = "%d-%s" % (current_g.label, current_node_index)
                            G.add_edge(u, v)
                            subnode_set.add(v)
                break

    for current_g in graphs:
        for current_node_index, current_node in enumerate(current_g.members):
            v = "%d-%s" % (current_g.label, current_node_index)
            if v in subnode_set:
                continue
            context[current_node] = True
            # context[v] = "%s[%d]" % (current_g.css_head(), current_node_index)
            G.add_node(current_g.label)
            logging.debug("set as root %s", current_node)
    return G


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
