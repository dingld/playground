import json
from datetime import datetime
from typing import List
from urllib3.util import parse_url

from scraperx.entities.html_parser import HtmlRuleResponseEntity, HtmlRuleRequestEntity
from scraperx.entities.task import TaskResponseModel, TaskRequestEntity, TaskStatus
from scraperx.model.html_parer import HtmlRuleModel
from scraperx.model.task import TaskModel
from scraperx.utils.parser_ml.feature import HtmlNode, HtmlClusterGraph


def convert_task_response_model(item: TaskModel) -> TaskResponseModel:
    return TaskResponseModel.construct(id=item.id, name=item.name, cron=item.cron,
                                       start_urls=json.loads(item.start_urls), status=item.status,
                                       created_at=item.created_at, updated_at=item.updated_at)


def convert_task_resquest_model(request: TaskRequestEntity) -> TaskModel:
    model = TaskModel()
    model.name = request.name
    model.cron = request.cron
    model.start_urls = json.dumps(request.start_urls)
    model.status = TaskStatus.debug
    model.updated_at = datetime.now()
    return model


def convert_request_to_html_rule_model(entity: HtmlRuleRequestEntity) -> HtmlRuleModel:
    model = HtmlRuleModel()
    model.name = entity.name
    model.domain = entity.domain
    model.path = entity.path
    model.type = entity.type
    model.ttl = entity.ttl
    model.rules = json.dumps(entity.rules)
    model.status = entity.status
    model.updated_at = datetime.now()
    return model


def convert_model_to_html_rule_response_entity(model: HtmlRuleModel) -> HtmlRuleResponseEntity:
    entity = HtmlRuleResponseEntity.construct(
        id=model.id,
        name=model.name,
        domain=model.domain,
        path=model.path,
        type=model.type,
        rules=json.loads(model.rules),
        ttl=model.ttl,
        status=model.status,
        updated_at=model.updated_at,
        created_at=model.created_at
    )
    return entity


def convert_html_node_to_data(node: HtmlNode) -> dict:
    return node.dict()


def convert_html_node_group_to_rule(label: int, nodes: List[HtmlNode], url: str) -> HtmlRuleRequestEntity:
    urlpart = parse_url(url)
    g = HtmlClusterGraph(label, nodes)
    return HtmlRuleRequestEntity.construct(
        id=label,
        name=g.css_head(),
        domain=urlpart.netloc,
        path=urlpart.current_file,
        type=0,
        ttl=60 * 60 * 24,
        rules=[],
    )
