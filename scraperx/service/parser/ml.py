import logging
import math
import re
from typing import List, Dict

from scraperx.entities.html_scrape import HtmlScrapeResultEntity
from scraperx.utils.converter import convert_html_node_to_data, convert_html_node_group_to_rule
from scraperx.service.parser import ml_train as train
from scraperx.service.parser.ml_feature import HtmlNode

logger = logging.getLogger(__name__)


def parse_html_ml(html: str, url: str, css="*[class]", eps: float = 0.2,
                  root: bool = True, href: bool = True, degrade_css: str = "*") -> List[HtmlScrapeResultEntity]:
    feature = train.parse_as_nodes(html, url, css=css)
    logger.info("parse html ml css=%s, eps=%s, feature=%d, url=%s", css, eps, len(feature), url)
    if not feature:
        css = degrade_css
        feature = train.parse_as_nodes(html, url, css=css)
        logger.info("retrying parse html ml css=%s, eps=%s, feature=%d, url=%s", css, eps, len(feature), url)
    if not feature:
        return []
    cluster = train.do_dbscan(train.nodes_as_array(feature), eps=eps)
    results = []
    group: Dict[int, List[HtmlNode]] = dict()
    for index, label in enumerate(cluster.labels_):
        if label == -1:
            logger.debug("skipping label -1: %s", feature[index].dict())
            continue
        node = feature[index]
        if href and not node.sel.css("*[href]"):
            logger.debug("skipping href null: %s", feature[index].dict())
            continue
        group.setdefault(label, []).append(node)
    ctx = dict()
    train.build_cluster_graph(group, ctx)
    for label, items in group.items():
        if root and not ctx.get(label):
            continue
        results.append(HtmlScrapeResultEntity.construct(
            url=url,
            rule=convert_html_node_group_to_rule(label, items, url),
            data=list(map(convert_html_node_to_data, items))
        ))
    for entity in results:
        for item in entity.data:
            item['text'] = re.sub("\n+[\r\n\t\s ]+", "\n", item['text'])
            item['text'] = re.sub("\t+[\t\s ]+", "\t", item['text'])
            item['text'] = re.sub("[\s ]+", " ", item['text'])
    return sorted(results, key=lambda x: sum(map(lambda item: len(item['text']), x.data)) / math.sqrt(len(x.data)),
                  reverse=True)
