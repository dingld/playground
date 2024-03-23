from datetime import datetime
from typing import List

from pydantic import BaseModel


class HtmlRuleType:
    link = 10
    item = 20


class HtmlRuleStatus:
    debug: int = 0
    ready: int = 10
    pause: int = 20

    @staticmethod
    def is_legal(status: int) -> bool:
        return HtmlRuleStatus.debug <= status <= HtmlRuleStatus.pause


class HtmlRuleRequestEntity(BaseModel):
    id: int = 0
    name: str
    domain: str
    path: str
    type: int
    ttl: int
    rules: list
    status: int = HtmlRuleStatus.debug
    html: str = ""
    created_at: datetime = None
    updated_at: datetime = None


class HtmlRuleResponseEntity(HtmlRuleRequestEntity):
    id: int
    created_at: datetime
    updated_at: datetime


class HtmlRuleListResponseEntity(BaseModel):
    total: int
    page: int
    size: int
    data: List[HtmlRuleResponseEntity]


class HtmlRuleSingleResponseEntity(BaseModel):
    ok: int
    data: HtmlRuleResponseEntity = None


class HtmlRuleCreateUpdateResponseEntity(BaseModel):
    ok: int
    message: str = ""
    data: HtmlRuleResponseEntity = None


class HtmlRuleDeleteResponseEntity(BaseModel):
    ok: int
    message: str = ""


class HtmlRuleToggleResponseEntity(BaseModel):
    ok: int
    message: str = ""
    data: HtmlRuleResponseEntity = None
