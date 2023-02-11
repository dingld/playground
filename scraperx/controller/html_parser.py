from fastapi import FastAPI

from scraperx.entities.html_parser import HtmlRuleRequestEntity, HtmlRuleListResponseEntity, \
    HtmlRuleSingleResponseEntity, HtmlRuleCreateUpdateResponseEntity, HtmlRuleDeleteResponseEntity, \
    HtmlRuleToggleResponseEntity, HtmlRuleStatus
from scraperx.service import html_parser_service

app = FastAPI()


@app.get("/")
async def list_page_size(page: int = 1, size: int = 10) -> HtmlRuleListResponseEntity:
    return html_parser_service.list_by_page_size(page=page, size=size)


@app.get("/{rule_id}")
async def get_by_id(rule_id: int) -> HtmlRuleSingleResponseEntity:
    return html_parser_service.get_by_id(rule_id=rule_id)


@app.post("/")
async def create_rule(request: HtmlRuleRequestEntity) -> HtmlRuleCreateUpdateResponseEntity:
    return html_parser_service.create_obj(request)


@app.post("/{rule_id}")
async def update_rule(rule_id: int, request: HtmlRuleRequestEntity) -> HtmlRuleCreateUpdateResponseEntity:
    return html_parser_service.update_obj(rule_id=rule_id, request=request)


@app.delete("/{rule_id}")
async def delete_task(rule_id: int) -> HtmlRuleDeleteResponseEntity:
    return html_parser_service.delete_by_id(rule_id=rule_id)


@app.post("/{rule_id}/toggle/{status}")
async def toggle_task(rule_id: int, status: int) -> HtmlRuleToggleResponseEntity:
    if not HtmlRuleStatus.is_legal(status):
        return HtmlRuleToggleResponseEntity.construct(ok=1, message="ilegal status")
    return html_parser_service.toggle_start_stop(rule_id=rule_id, status=status)
