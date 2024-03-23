from typing import List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from scraperx.entities.scrape import HtmlScrapeResultEntity
from scraperx.service import validate

app = FastAPI()


@app.get("/rule/{rule_id}")
async def parse_with_rule_id(rule_id: int) -> HtmlScrapeResultEntity:
    return validate.parse_with_rule_id(rule_id)


@app.get("/cluster/{rule_id}")
async def parse_with_rule_id(rule_id: int) -> List[HtmlScrapeResultEntity]:
    return validate.parse_with_cluster(rule_id)


@app.get("/cluster/{rule_id}/html")
async def parse_with_rule_id(rule_id: int) -> HTMLResponse:
    html = validate.parse_html_cluster_markers(rule_id)
    return HTMLResponse(content=html, status_code=200)
