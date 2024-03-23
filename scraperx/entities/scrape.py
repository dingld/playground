from typing import List

from pydantic import BaseModel

from scraperx.entities.rule import HtmlRuleRequestEntity


class HtmlScrapeParseRequestEntity(BaseModel):
    html: str
    url: str
    rule: HtmlRuleRequestEntity


class HtmlScrapeResultEntity(BaseModel):
    url: str
    rule: HtmlRuleRequestEntity
    data: List[dict]
    status: int = 0
    msg: str = "ok"


class HtmlScrapeParseFactoryRequestEntity(BaseModel):
    html: str
    url: str
