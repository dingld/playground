from typing import List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from scraperx.entities.scrape import HtmlScrapeParseRequestEntity, HtmlScrapeResultEntity, \
    HtmlScrapeParseFactoryRequestEntity
from scraperx.service import downloader
from scraperx.service.parser.sql import parse_html_with_rules, parse_html_with_rule
from scraperx.service.parser.cluster import parse_html_cluster

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
    html = await downloader.download_html(url)
    return HTMLResponse(html)


@app.get("/html_and_parse")
async def download_and_parse(url: str) -> List[HtmlScrapeResultEntity]:
    html = await downloader.download_html(url)
    return parse_html_with_rules(html, url)


@app.get("/html_and_ml")
async def download_and_ml(url: str, eps: float = 0.2, css: str = "*[class]",
                          root: bool = False, href: bool = True) -> List[HtmlScrapeResultEntity]:
    html = await downloader.download_html(url)
    return parse_html_cluster(html, url, eps=eps, css=css, root=root, href=href)


@app.post("/parse")
async def parse(request: HtmlScrapeParseRequestEntity) -> HtmlScrapeResultEntity:
    return parse_html_with_rule(html=request.html, url=request.url, rule=request.rule)


@app.post("/parse_factory")
async def parse_factory(request: HtmlScrapeParseFactoryRequestEntity) -> List[HtmlScrapeResultEntity]:
    return parse_html_with_rules(html=request.html, url=request.url)


@app.post("/parse_ml")
async def parse_ml(eps: float = 0.2,
                   css: str = "*[class]", root: bool = False, href: bool = True,
                   request: HtmlScrapeParseFactoryRequestEntity = None) -> List[
    HtmlScrapeResultEntity]:
    return parse_html_cluster(html=request.html, url=request.url, eps=eps, css=css, root=root, href=href)

