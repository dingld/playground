from fastapi import FastAPI

from scraperx.entities.rule import HtmlRuleRequestEntity, HtmlRuleListResponseEntity, \
    HtmlRuleSingleResponseEntity, HtmlRuleCreateUpdateResponseEntity, HtmlRuleDeleteResponseEntity, \
    HtmlRuleToggleResponseEntity, HtmlRuleStatus
from scraperx.service import rule as rule_service

app = FastAPI()


@app.get("/")
async def list_page_size(page: int = 1, size: int = 10) -> HtmlRuleListResponseEntity:
    return rule_service.get_by_page_size(page=page, size=size)


@app.get("/{rule_id}")
async def get_by_id(rule_id: int) -> HtmlRuleSingleResponseEntity:
    return rule_service.get_by_id(rule_id=rule_id)


@app.post("/")
async def create_rule(request: HtmlRuleRequestEntity) -> HtmlRuleCreateUpdateResponseEntity:
    return rule_service.create_obj(request)


@app.put("/{rule_id}")
async def update_rule(rule_id: int, request: HtmlRuleRequestEntity) -> HtmlRuleCreateUpdateResponseEntity:
    return rule_service.update_obj(rule_id=rule_id, request=request)


@app.delete("/{rule_id}")
async def delete_rule(rule_id: int) -> HtmlRuleDeleteResponseEntity:
    return rule_service.delete_by_id(rule_id=rule_id)


@app.post("/{rule_id}/toggle/{status}")
async def toggle_task(rule_id: int, status: int) -> HtmlRuleToggleResponseEntity:
    if not HtmlRuleStatus.is_legal(status):
        return HtmlRuleToggleResponseEntity.construct(ok=1, message="illegal status")
    return rule_service.toggle_start_stop(rule_id=rule_id, status=status)


@app.put("/{rule_id}/html")
async def update_rule(rule_id: int, request: HtmlRuleRequestEntity) -> HtmlRuleCreateUpdateResponseEntity:
    return rule_service.update_html(rule_id=rule_id, html=request.html)
