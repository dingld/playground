"""
1. task CRUD
2. task start/stop
3. task progress
"""

from fastapi import FastAPI
from sqlalchemy.orm import Session

from scraperx.dao.session import SessionLocal
from scraperx.entities.task import TaskListResponses, TaskCreateResponse, TaskDeleteResponse, TaskToggleResponse
from scraperx.entities.task import TaskResponseModel, TaskRequestModel, TaskStatus
from scraperx.model.task import TaskModel
from scraperx.utils.converter import convert_task_response_model, convert_task_resquest_model

app = FastAPI()


@app.get("/")
async def list_project(page: int = 1, size: int = 10) -> TaskListResponses:
    session: Session = SessionLocal()
    total = session.query(TaskModel).count()
    query = session.query(TaskModel).limit(size)
    if page > 1:
        query = query.offset(page * size - size)
    data = list(map(convert_task_response_model, query.all()))
    return TaskListResponses.construct(total=total, page=page, size=size, data=data)


@app.get("/{task_id}")
async def get_task(task_id: int) -> TaskResponseModel:
    session: Session = SessionLocal()
    item = session.query(TaskModel).filter_by(id=task_id).first()
    if not item:
        return {}

    return convert_task_response_model(item)


@app.post("/")
async def create_task(request: TaskRequestModel) -> TaskCreateResponse:
    model = convert_task_resquest_model(request)
    with SessionLocal() as session:
        if session.query(TaskModel).filter_by(name=request.name).count():
            return TaskCreateResponse.construct(status=1, message="task already exists")
        session.add(model)
    return TaskCreateResponse.construct(status=0, data=convert_task_response_model(model))


@app.put("/{task_id}")
async def update_task(task_id: int, request: TaskRequestModel) -> TaskCreateResponse:
    model = convert_task_resquest_model(request)
    model.id = task_id
    with SessionLocal() as session:
        if session.query(TaskModel).filter_by(id=task_id).count() == 0:
            return TaskCreateResponse.construct(status=1, message="task not exists")
        session.merge(model)
    return TaskCreateResponse.construct(status=0, data=convert_task_response_model(model))


@app.delete("/{task_id}")
async def delete_task(task_id: int) -> TaskDeleteResponse:
    with SessionLocal() as session:
        obj = session.query(TaskModel).filter_by(id=task_id).first()
        if not obj:
            return TaskDeleteResponse.construct(status=1, message="task not exists")
        session.delete(obj)
    return TaskDeleteResponse.construct(status=0)


@app.post("/{task_id}/toggle/{status}")
async def toggle_task(task_id: int, status: int) -> TaskToggleResponse:
    if not TaskStatus.is_legal(status):
        return TaskToggleResponse.construct(status=1, message="ilegal status")
    with SessionLocal() as session:
        obj: TaskModel = session.query(TaskModel).filter_by(id=task_id).first()
        if not obj:
            return TaskToggleResponse.construct(status=1, message="task not exists")
        obj.status = status
        session.delete(obj)
    return TaskToggleResponse.construct(status=0)
