"""
multiple scrape endpoints
1. download url
2. scrape once -> links & items
3. crawl: scrape -> schedule -> save
"""
import logging
import math
import re
from typing import List, Dict

import urllib3.util
from httpx import AsyncClient
from urllib3.util.url import Url

from scraperx.entities.html_parser import HtmlRuleRequestEntity
from scraperx.entities.html_scrape import HtmlScrapeResultEntity
from scraperx.service.parser_service import get_all
from scraperx.utils.converter import convert_html_node_to_data, convert_html_node_group_to_rule
from scraperx.utils.parser_ml import train
from scraperx.utils.parser_ml.feature import HtmlNode
from scraperx.utils.parser_sqlite3 import init_sqlite3_conn, init_sqlite3_source, query_sqlite3_parser

logger = logging.getLogger("service.scrape")


async def download_html(url: str, method: str = "GET") -> str:
    logging.info("downloading html %s", url)
    async with AsyncClient() as client:
        client.headers[
            'User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        resp = await client.request(method, url)
        await resp.aread()
        return resp.text


def parse_html_with_rule(html: str, url: str, rule: HtmlRuleRequestEntity) -> HtmlScrapeResultEntity:
    conn = init_sqlite3_conn()
    init_sqlite3_source(conn, source=html, base_url=url)
    data = []
    for sql in rule.rules:
        data.extend(query_sqlite3_parser(sql=sql, conn=conn))
    return HtmlScrapeResultEntity.construct(rule=rule, data=data, url=url)


def parse_html_with_rule_factory(html: str, url: str) -> List[HtmlScrapeResultEntity]:
    url_part: Url = urllib3.util.parse_url(url)
    logger.info("scrape url netloc=%s, path=%s", url_part.netloc, url_part.path)
    items = []
    for rule in get_all():
        if rule.domain in url_part.netloc and rule.path in url_part.path:
            items.append(parse_html_with_rule(html, url, rule))
    return items


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
