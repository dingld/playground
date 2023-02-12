import re
from dataclasses import dataclass
from itertools import takewhile
from typing import Dict, List

from lxml.etree import ElementTree
from lxml.html import HtmlElement
from parsel import Selector


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
                   class_name=attrib.pop("class", ""),
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
        for x in self.attrib:
            item["attrib.%s" % x] = 1
        for y in self.children:
            item["children.%s" % y] = 1
        item['xpath'] = self.xpath_strim()
        return item

    def dict(self):
        d = dict(
            tag=self.tag,
            class_name=self.class_name,
        )
        d.update(self.attrib)
        d.update(html=self.sel.xpath(".").extract_first())
        d.update(text=self.sel.xpath("string(.)").extract_first())

        return d

    def xpath_strim(self):
        path = self.xpath()
        return re.sub("\[\d+\]", "", path)

    def xpath(self):
        return self.tree.getpath(self.html_element)

    def parent(self):
        return HtmlNode.from_element(self.html_element.getparent(), self.tree)

    def has_ancestor(self, node):
        return node.xpath() in self.xpath()

    def has_ancestor_in(self, nodes):
        return any([self.has_ancestor(node) for node in nodes])

    def __str__(self):
        return "%s.%s" % (self.tag, self.class_name)

    __repr__ = __str__


class HtmlNodeGraph:

    def __init__(self, label: int, members: List[HtmlNode]):
        self.label = label
        self.members = members
        self._xpath = ""
        self._depth = 0

    def head(self):
        path = self.xpath()
        if not path.startswith("/"):
            path = "/" + path

        parent_path, tag = path.rsplit("/", maxsplit=1)
        tree = self.members[0].tree
        nodes = tree.xpath(parent_path)
        node = nodes[0]
        attrib = dict(node.attrib)
        if attrib.get("id"):
            return "#%s > %s" % (attrib['id'], tag)
        if attrib.get("class"):
            return "%s.%s > %s" % (node.tag, attrib['class'], tag)
        return path

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
        for member in self.members:
            if not member.has_ancestor_in(graph.members):
                return False
        return True

    def __len__(self):
        return len(self.members)


def longest_common_prefix(prefixes: List[str]) -> str:
    res = ''.join(c[0] for c in takewhile(lambda x: all(x[0] == y for y in x), zip(*prefixes)))
    return res
