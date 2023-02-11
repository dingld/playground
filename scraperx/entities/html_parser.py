from datetime import datetime
from typing import List

from pydantic import BaseModel


class HtmlRuleType:
    link = 0
    item = 1


class HtmlRuleStatus:
    debug: int = 0
    start: int = 10
    stop: int = 20

    @staticmethod
    def is_legal(status: int) -> bool:
        return HtmlRuleStatus.debug <= status <= HtmlRuleStatus.stop



class HtmlRuleRequestEntity(BaseModel):
    name: str
    domain: str
    path: str
    type: int
    rules: str
    created_at: datetime
    updated_at: datetime


class HtmlRuleResponseEntity(BaseModel):
    name: str
    domain: str
    path: str
    type: int
    rules: list
    created_at: datetime
    updated_at: datetime


class HtmlRuleListResponseEntity(BaseModel):
    total: int
    page: int
    size: int
    data: List[HtmlRuleResponseEntity]


class HtmlRuleSingleResponseEntity(BaseModel):
    ok: int
    data: List[HtmlRuleResponseEntity]


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
