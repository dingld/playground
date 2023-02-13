import logging
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
        # for x in self.attrib:
        #     item["attrib.%s" % x] = 1
        #
        # for y in self.children:
        #     item["children.%s" % y] = 1

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
                    logging.debug("esacpe key %s: %s -> %s", key, new_key, new_value)
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
            return "#.%s" % id
        class_name = dict(element.attrib).get("class", "")
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
