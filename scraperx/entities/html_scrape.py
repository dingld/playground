from typing import List

from scraperx.entities.html_parser import HtmlRuleRequestEntity


class HtmlScrapeResultEntity(HtmlRuleRequestEntity):
    rule: HtmlRuleRequestEntity
    data: List[dict]
