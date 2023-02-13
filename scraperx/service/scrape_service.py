"""
multiple scrape endpoints
1. download url
2. scrape once -> links & items
3. crawl: scrape -> schedule -> save
"""
from httpx import AsyncClient

from scraperx.entities.html_parser import HtmlRuleRequestEntity
from scraperx.entities.html_scrape import HtmlScrapeResultEntity
from scraperx.utils.parser_sqlite3 import init_sqlite3_conn, init_sqlite3_source, query_sqlite3_parser


async def download(url: str, method: str) -> str:
    async with AsyncClient() as client:
        resp = await client.request(method, url)
        await resp.aread()
        return resp.text


def scrape(html: str, url: str, rule: HtmlRuleRequestEntity):
    conn = init_sqlite3_conn()
    init_sqlite3_source(conn, source=html, base_url=url)
    data = []
    for sql in rule.rules:
        data.extend(query_sqlite3_parser(sql=sql, conn=conn))
    return HtmlScrapeResultEntity.construct(rule=rule, data=data)


async def crawl(task_id: int):
    pass
