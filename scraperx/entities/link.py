from pydantic import BaseModel
from sqlalchemy import DateTime
from typing import List


class LinkStatus:
    PENDING = 0
    QUEUED = 10
    DONE = 20
    ERROR = 30


class LinkRequestEntity(BaseModel):
    task_id: str
    fingerprint: str
    domain: str
    url: str
    status_code: int


class LinkResponseEntity(BaseModel):
    id: int
    task_id: str
    fingerprint: str
    domain: str
    url: str
    response_body_size: str
    status_code: int
    retry: int
    error: str
    created_at: DateTime
    updated_at: DateTime
    fetched_at: DateTime


class LinkSingleResponseEntity(BaseModel):
    ok: int
    message: int
    data: LinkResponseEntity = None


class LinkListResponseEntity(BaseModel):
    total: int
    page: int
    size: int
    data: List[LinkResponseEntity]


class LinkCreateUpdateResponseEntity(BaseModel):
    ok: int
    message: str = ""
    data: List[LinkResponseEntity] = None


class LinkDeleteResponseEntity(BaseModel):
    ok: int
    message: str = ""
    data: List[LinkResponseEntity] = None
