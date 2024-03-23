import logging
import re

from parsel import Selector

logger = logging.getLogger("html_extract")


def to_simple_text(text: str):
    text = re.sub("\n+[\r\n\t\s ]+", "\n", text)
    text = re.sub("\t+[\t\s ]+", "\t", text)
    text = re.sub("[\s ]+", " ", text)
    return text.strip()


def selector_to_text(html: str, css: str):
    sel = Selector(text=html, base_url="http://www.test.com")
    logger.debug("extract css=%s: %s", css, html)
    return sel.css(css).xpath("string()").extract_first()


def selector_to_attr(html: str, css: str, attr: str):
    sel = Selector(text=html, base_url="http://www.test.com")
    logger.debug("extract css=%s: %s", css, html)
    for node in sel.css(css):
        node: Selector = node
        attrib: dict = dict(node.root.attrib)
        if attrib.get(attr):
            return attrib.get(attr)
    return
