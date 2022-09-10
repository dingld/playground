import re
from dataclasses import dataclass
from itertools import takewhile
from typing import Dict, List

from lxml.etree import ElementTree
from lxml.html import HtmlElement


@dataclass
class HtmlNode:
    tag: str
    class_name: str
    attrib: Dict[str, str]
    children: List
    html_element: HtmlElement
    tree: ElementTree

    @classmethod
    def from_element(cls, node: HtmlElement, tree: ElementTree):
        attrib = dict(node.attrib)
        return cls(tag=node.tag,
                   class_name=attrib.pop("class", ""),
                   attrib=attrib,
                   children=list(map(lambda x: cls.from_element(x, tree), node.getchildren())),
                   html_element=node,
                   tree=tree
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

    def xpath_strim(self):
        path = self.xpath()
        return re.sub("\[\d+\]", "", path)

    def xpath(self):
        return self.tree.getpath(self.html_element)

    def parent(self):
        return HtmlNode.from_element(self.html_element.getparent(), self.tree)

    def has_ancestor(self, node):
        return self.xpath() in node.xpath()

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


def longest_common_prefix(prefixes: List[str]) -> str:
    res = ''.join(c[0] for c in takewhile(lambda x: all(x[0] == y for y in x), zip(*prefixes)))
    return res
