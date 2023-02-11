from datetime import datetime
from typing import List

from pydantic import BaseModel


class TaskStatus:
    debug: int = 0
    start: int = 10
    stop: int = 20

    @staticmethod
    def is_legal(status: int) -> bool:
        return TaskStatus.debug <= status <= TaskStatus.stop


class TaskRequestEntity(BaseModel):
    name: str
    start_urls: List[str]
    cron: str
    status: int


class TaskResponseModel(BaseModel):
    id: int
    name: str
    start_urls: List[str]
    cron: str
    status: int
    created_at: datetime
    updated_at: datetime


class TaskListResponseEntity(BaseModel):
    total: int
    page: int
    size: int
    data: List[TaskResponseModel]


class TaskSingleResponseEntity(BaseModel):
    ok: int
    data: TaskResponseModel = None


class TaskCreateUpdateResponseEntity(BaseModel):
    ok: int
    message: str = ""
    data: TaskResponseModel = None


class TaskDeleteResponseEntity(BaseModel):
    ok: int
    message: str = ""


class TaskToggleResponseEntity(BaseModel):
    ok: int
    message: str = ""
    data: TaskResponseModel = None
