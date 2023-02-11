import json
from datetime import datetime
from scraperx.entities.task import TaskResponseModel, TaskRequestEntity, TaskStatus
from scraperx.entities.html_parser import HtmlRuleResponseEntity, HtmlRuleRequestEntity
from scraperx.model.task import TaskModel
from scraperx.model.html_parer import HtmlRuleModel


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


def convert_html_rule_model(entity: HtmlRuleRequestEntity) -> HtmlRuleModel:
    model = HtmlRuleModel()
    model.name = entity.name
    model.domain = entity.domain
    model.path = entity.path
    model.type = entity.type
    model.rules = json.dumps(entity.rules)
    model.updated_at = datetime.now()
    return model


def convert_to_html_rule_response_entity(model: HtmlRuleModel) -> HtmlRuleResponseEntity:
    entity = HtmlRuleResponseEntity()
    entity.name = model.name
    entity.domain = model.domain
    entity.path = model.path
    entity.type = model.type
    entity.rules = model.rules

    model.updated_at = model.updated_at
    entity.created_at = model.created_at
    return entity
