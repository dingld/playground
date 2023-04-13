from fastapi import FastAPI

from scraperx.entities.html_parser import HtmlRuleRequestEntity, HtmlRuleListResponseEntity, \
    HtmlRuleSingleResponseEntity, HtmlRuleCreateUpdateResponseEntity, HtmlRuleDeleteResponseEntity, \
    HtmlRuleToggleResponseEntity, HtmlRuleStatus
from scraperx.service import parser_rule

app = FastAPI()


@app.get("/")
async def list_page_size(page: int = 1, size: int = 10) -> HtmlRuleListResponseEntity:
    return parser_rule.get_by_page_size(page=page, size=size)


@app.get("/{rule_id}")
async def get_by_id(rule_id: int) -> HtmlRuleSingleResponseEntity:
    return parser_rule.get_by_id(rule_id=rule_id)


@app.post("/")
async def create_rule(request: HtmlRuleRequestEntity) -> HtmlRuleCreateUpdateResponseEntity:
    return parser_rule.create_obj(request)


@app.put("/{rule_id}")
async def update_rule(rule_id: int, request: HtmlRuleRequestEntity) -> HtmlRuleCreateUpdateResponseEntity:
    return parser_rule.update_obj(rule_id=rule_id, request=request)


@app.delete("/{rule_id}")
async def delete_task(rule_id: int) -> HtmlRuleDeleteResponseEntity:
    return parser_rule.delete_by_id(rule_id=rule_id)


@app.post("/{rule_id}/toggle/{status}")
async def toggle_task(rule_id: int, status: int) -> HtmlRuleToggleResponseEntity:
    if not HtmlRuleStatus.is_legal(status):
        return HtmlRuleToggleResponseEntity.construct(ok=1, message="illegal status")
    return parser_rule.toggle_start_stop(rule_id=rule_id, status=status)
