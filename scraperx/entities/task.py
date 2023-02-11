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


class TaskRequestModel(BaseModel):
    id: int
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


class TaskListResponses(BaseModel):
    total: int
    page: int
    size: int
    data: List[TaskResponseModel]


class TaskCreateResponse(BaseModel):
    ok: int
    message: str
    data: TaskResponseModel


class TaskDeleteResponse(BaseModel):
    ok: int
    message: str


class TaskToggleResponse(BaseModel):
    ok: int
    message: str
