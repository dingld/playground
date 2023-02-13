from typing import List

from pydantic import BaseModel

from scraperx.entities.html_parser import HtmlRuleRequestEntity


class HtmlScrapeParseRequestEntity(BaseModel):
    html: str
    url: str
    rule: HtmlRuleRequestEntity


class HtmlScrapeResultEntity(BaseModel):
    url: str
    rule: HtmlRuleRequestEntity
    data: List[dict]


class HtmlScrapeParseFactoryRequestEntity(BaseModel):
    html: str
    url: str
