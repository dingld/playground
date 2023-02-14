"""
1. fetch start urls from task
2. parse html
    a>. links
    b>. items
3.
"""
from typing import List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from scraperx.entities.html_scrape import HtmlScrapeParseRequestEntity, HtmlScrapeResultEntity, \
    HtmlScrapeParseFactoryRequestEntity
from scraperx.service import scrape_service

app = FastAPI()


@app.get("/")
async def index() -> JSONResponse:
    return JSONResponse(content=(
        dict(
            html="html",
            parse="parse"
        )
    ))


@app.get("/html")
async def download(url: str) -> HTMLResponse:
    html = await scrape_service.download_html(url)
    return HTMLResponse(html)


@app.get("/html_and_parse")
async def download_and_parse(url: str) -> List[HtmlScrapeResultEntity]:
    html = await scrape_service.download_html(url)
    return scrape_service.parse_html_with_rule_factory(html, url)


@app.get("/html_and_ml")
async def download_and_ml(url: str, eps: float = 0.2, css: str = "*[class]", root: bool = False, href: bool = True) -> \
List[
    HtmlScrapeResultEntity]:
    html = await scrape_service.download_html(url)
    return scrape_service.parse_html_ml(html, url, eps=eps, css=css, root=root, href=href)


@app.post("/parse")
async def parse(request: HtmlScrapeParseRequestEntity) -> HtmlScrapeResultEntity:
    return scrape_service.parse_html_with_rule(html=request.html, url=request.url, rule=request.rule)


@app.post("/parse_factory")
async def parse_factory(request: HtmlScrapeParseFactoryRequestEntity) -> List[HtmlScrapeResultEntity]:
    return scrape_service.parse_html_with_rule_factory(html=request.html, url=request.url)


@app.post("/parse_ml")
async def parse_ml(eps: float = 0.2,
                   css: str = "*[class]", root: bool = False, href: bool = True,
                   request: HtmlScrapeParseFactoryRequestEntity = None) -> List[
    HtmlScrapeResultEntity]:
    return scrape_service.parse_html_ml(html=request.html, url=request.url, eps=eps, css=css, root=root, href=href)


@app.get("/crawler/{task_id}/start")
async def schedule_start_urls(task_id: int, delay: bool = True):
    pass


@app.get("/crawler/{task_id}/schedule")
async def schedule_next_urls(task_id: int, count: int = 1, delay: bool = True):
    pass


@app.post("/{task_id}/crawler/schedule")
async def schedule_urls(task_id: int, ):
    pass


@app.post("/{task_id}/crawler/retry")
async def schedule_retry_policy(task_id: int, max_retry: int = 3, delay: int = 60):
    pass
