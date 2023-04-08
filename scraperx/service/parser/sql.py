import logging
from typing import List

import urllib3.util
from urllib3.util.url import Url

from scraperx.entities.html_parser import HtmlRuleRequestEntity
from scraperx.entities.html_scrape import HtmlScrapeResultEntity
from scraperx.service.parser_rule import get_all
from scraperx.utils.parser_sqlite3 import init_sqlite3_conn, init_sqlite3_source, query_sqlite3_parser

logger = logging.getLogger(__name__)


def parse_html_with_rule(html: str, url: str, rule: HtmlRuleRequestEntity) -> HtmlScrapeResultEntity:
    conn = init_sqlite3_conn()
    init_sqlite3_source(conn, source=html, base_url=url)
    data = []
    for sql in rule.rules:
        data.extend(query_sqlite3_parser(sql=sql, conn=conn))
    return HtmlScrapeResultEntity.construct(rule=rule, data=data, url=url)


def parse_html_with_rules(html: str, url: str) -> List[HtmlScrapeResultEntity]:
    url_part: Url = urllib3.util.parse_url(url)
    logger.info("scrape url netloc=%s, path=%s", url_part.netloc, url_part.path)
    items = []
    for rule in get_all():
        if rule.domain in url_part.netloc and rule.path in url_part.path:
            items.append(parse_html_with_rule(html, url, rule))
    return items
