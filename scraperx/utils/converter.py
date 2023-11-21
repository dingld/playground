import json
from datetime import datetime
from typing import List

from urllib3.util import parse_url

from scraperx.entities.link import LinkRequestEntity, LinkResponseEntity
from scraperx.entities.rule import HtmlRuleResponseEntity, HtmlRuleRequestEntity
from scraperx.entities.task import TaskResponseModel, TaskRequestEntity, TaskStatus
from scraperx.model.link import LinkModel
from scraperx.model.rule import HtmlRuleModel
from scraperx.model.task import TaskModel
from scraperx.service.parser._cluster import HtmlNode, HtmlClusterGraph


def convert_link_request_to_model(request: LinkRequestEntity) -> LinkModel:
    model = LinkModel()
    model.task_id = request.task_id
    model.fingerprint = request.fingerprint
    model.domain = request.domain
    model.url = request.url
    return model


def convert_link_response_to_model(response: LinkResponseEntity) -> LinkModel:
    model = LinkModel()
    model.id = response.id
    model.task_id = response.task_id
    model.fingerprint = response.fingerprint
    model.domain = response.domain
    model.url = response.url
    model.response_body_size = response.response_body_size
    model.status_code = response.status_code
    model.retry = response.retry
    model.error = response.error
    model.created_at = response.created_at
    model.updated_at = response.updated_at
    model.fetched_at = response.fetched_at
    return model


def convert_link_model_to_response(item: LinkModel) -> LinkResponseEntity:
    return LinkResponseEntity.construct(id=item.id, task_id=item.task_id, fingerprint=item.fingerprint,
                                        domain=item.domain, url=item.url, response_body_size=item.response_body_size,
                                        status_code=item.status_code, retry=item.retry, error=item.error,
                                        created_at=item.created_at, updated_at=item.updated_at,
                                        fetched_at=item.fetched_at
                                        )


def convert_task_model_to_response(item: TaskModel) -> TaskResponseModel:
    return TaskResponseModel.construct(id=item.id, name=item.name, cron=item.cron,
                                       start_urls=json.loads(item.start_urls), status=item.status,
                                       created_at=item.created_at, updated_at=item.updated_at)


def convert_task_request_model(request: TaskRequestEntity) -> TaskModel:
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
        path=urlpart.path,
        type=0,
        ttl=60 * 60 * 24,
        rules=[],
    )
