import logging
import re
from dataclasses import dataclass
from itertools import takewhile
from typing import Dict, List

import networkx as nx
import pandas as pd
from lxml import etree
from lxml.etree import ElementTree
from lxml.html import HtmlElement
from parsel import Selector
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import OneHotEncoder

logger = logging.getLogger("parser.cluster")


def filter_classname(classname: str) -> str:
    return re.sub("[\s]+", " ", classname.strip())


@dataclass
class HtmlNode:
    tag: str
    class_name: str
    attrib: Dict[str, str]
    children: List
    sel: Selector
    html_element: HtmlElement
    tree: ElementTree

    @classmethod
    def from_element(cls, sel: Selector, tree: ElementTree):
        node = sel.root
        attrib = dict(node.attrib)
        return cls(tag=node.tag,
                   class_name=filter_classname(attrib.pop("class", "")),
                   attrib=attrib,
                   children=list(map(lambda x: cls.from_element(x, tree), sel.xpath("./*"))),
                   sel=sel,
                   html_element=node,
                   tree=tree,
                   )

    def row(self):
        item = dict(
            tag=self.tag,
            class_name=self.class_name
        )

        item['head'] = self.get_head(self.html_element)
        for key, value in item.items():
            if isinstance(value, str):
                new_value = re.sub("[\d]{2,}", "+escape_numbers", value)
                if new_value != value:
                    logging.debug("esacpe %s value: %s -> %s", key, value, new_value)
                    item[key] = new_value
        for key, value in list(item.items()):
            if isinstance(key, str):
                new_key = re.sub("[\d]{2,}", "+escape_numbers", key)
                if new_key != key:
                    logging.debug("esacpe key %s -> %s", key, new_key)
                    item[new_key] = item.pop(key)
        return item

    def dict(self):
        d = dict(
            tag=self.tag,
            class_name=self.class_name,
        )
        for key, value in self.attrib.items():
            d["attr_" + key] = value
        d.update(text=self.sel.xpath("string(.)").extract_first())
        d['href'] = self.sel.css("a[href]::attr(href)").extract_first()
        return d

    def xpath_strim(self):
        path = self.xpath()
        return re.sub("\[\d+\]", "", path)

    def xpath(self):
        return self.tree.getpath(self.html_element)

    def depth(self):
        return self.get_depth(self.html_element)

    def parent(self):
        return HtmlNode.from_element(self.html_element.getparent(), self.tree)

    def has_ancestor(self, element: HtmlElement, step: int = 100):
        current_node = self.html_element
        while current_node != element and step > 0 and current_node is not None and self.get_depth(current_node) > 1:
            step -= 1
            parent = current_node.getparent()
            if parent == element:
                return True
            current_node = parent
        return False

    def get_css(self, step: int = 100, full: bool = False):
        cssselectors = []
        current_node = self.html_element
        while step > 0 and current_node is not None and self.get_depth(current_node) > 1:
            step -= 1
            head = self.get_head(current_node)
            cssselectors.append(head)
            if not full and "." in head:
                break
            current_node = current_node.getparent()
        return " > ".join(cssselectors[::-1])

    def has_ancestor_in(self, nodes):
        return any([self.has_ancestor(node.html_element) for node in nodes])

    def get_head(self, element: HtmlElement):
        id = dict(element.attrib).get("id", "")
        if id:
            return "#%s" % id
        class_name = filter_classname(dict(element.attrib).get("class", ""))
        if class_name:
            return "%s.%s" % (element.tag, ".".join(class_name.split(" ")))
        return element.tag

    def get_depth(self, element: HtmlElement):
        return len(self.tree.getpath(element).split("/"))

    def __str__(self):
        return self.get_head(self.html_element)

    __repr__ = __str__

    def __eq__(self, other):

        # Equality Comparison between two objects
        return self.xpath() == other.xpath()

    def __hash__(self):

        # hash(custom_object)
        return hash(self.xpath())


class HtmlClusterGraph:

    def __init__(self, label: int, members: List[HtmlNode]):
        self.label = label
        self.members = members
        self._xpath = ""
        self._depth = 0

    def head(self, full: bool = False):
        return "[%d] %s" % (self.label, self.css_head(full))

    def css_head(self, full: bool = False):
        return ",".join(set(map(lambda x: x.get_css(full=full), self.members)))

    def xpath(self):
        if not self._xpath:
            self._xpath = longest_common_prefix(list(map(lambda x: x.xpath(), self.members)))
        return self._xpath.strip("[/1234567890")

    def depth(self):
        if not self._depth:
            for member in self.members:
                path = member.xpath()
                self._depth = max(self._depth, len(path.split("/")))
        return self._depth

    def subgraph_to(self, graph):
        return all(map(lambda member: member.has_ancestor_in(graph.members),
                       self.members))

    def __len__(self):
        return len(self.members)


def longest_common_prefix(prefixes: List[str]) -> str:
    res = ''.join(c[0] for c in takewhile(lambda x: all(x[0] == y for y in x), zip(*prefixes)))
    return res


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
    return array_as_onehot_sparse(pd.DataFrame(rows))


def array_as_onehot_sparse(df: pd.DataFrame):
    vectors = OneHotEncoder(sparse=True).fit_transform(df)
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
