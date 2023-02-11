import json
from datetime import datetime
from scraperx.entities.task import TaskResponseModel, TaskRequestModel, TaskStatus
from scraperx.model.task import TaskModel


def convert_task_response_model(item: TaskModel) -> TaskResponseModel:
    return TaskResponseModel.construct(id=item.id, name=item.name, cron=item.cron,
                                       start_urls=json.loads(item.start_urls), status=item.status,
                                       created_at=item.created_at, updated_at=item.updated_at)


def convert_task_resquest_model(request: TaskRequestModel) -> TaskModel:
    model = TaskModel()
    model.name = request.name
    model.cron = request.cron
    model.start_urls = json.dumps(request.start_urls)
    model.status = TaskStatus.debug
    model.updated_at = datetime.now()
    return model
