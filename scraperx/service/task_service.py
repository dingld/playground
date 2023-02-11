import datetime
import json

from sqlalchemy.orm import Session

from scraperx.dao.session import SessionLocal
from scraperx.entities.task import TaskListResponseEntity, TaskCreateUpdateResponseEntity, TaskDeleteResponseEntity, \
    TaskToggleResponseEntity, TaskRequestEntity, TaskSingleResponseEntity
from scraperx.model.task import TaskModel
from scraperx.utils.converter import convert_task_response_model, convert_task_resquest_model


def get_by_id(task_id: int) -> TaskSingleResponseEntity:
    session: Session = SessionLocal()
    item = session.query(TaskModel).filter_by(id=task_id).first()
    if not item:
        return TaskSingleResponseEntity.construct(ok=1)

    return TaskSingleResponseEntity.construct(ok=0, data=convert_task_response_model(item))


def list_by_page_size(page: int, size: int) -> TaskListResponseEntity:
    session: Session = SessionLocal()
    total = session.query(TaskModel).count()
    query = session.query(TaskModel).limit(size)
    if page > 1:
        query = query.offset(page * size - size)
    data = list(map(convert_task_response_model, query.all()))
    return TaskListResponseEntity.construct(total=total, page=page, size=size, data=data)


def create_obj(request: TaskRequestEntity) -> TaskCreateUpdateResponseEntity:
    model = convert_task_resquest_model(request)
    with SessionLocal() as session:
        if session.query(TaskModel).filter_by(name=request.name).count():
            return TaskCreateUpdateResponseEntity.construct(ok=1, message="task already exists")
        model.created_at = model.updated_at
        session.add(model)
        session.commit()
        return TaskCreateUpdateResponseEntity.construct(ok=0, data=convert_task_response_model(model))


def update_obj(task_id: int, request: TaskRequestEntity) -> TaskCreateUpdateResponseEntity:
    with SessionLocal() as session:
        model: TaskModel = session.query(TaskModel).filter_by(id=task_id).first()
        if not model:
            return TaskCreateUpdateResponseEntity.construct(ok=1, message="task not exists")
        if model.name != request.name:
            if exist_by_name(session, request.name):
                return TaskCreateUpdateResponseEntity.construct(ok=1, message="rule name dupelicated")
        model.name = request.name
        model.cron = request.cron
        model.start_urls = json.dumps(request.start_urls)
        model.updated_at = datetime.datetime.now()
        session.merge(model)
        session.commit()
        return TaskCreateUpdateResponseEntity.construct(ok=0, data=convert_task_response_model(model))


def exist_by_name(session: SessionLocal, name: str) -> bool:
    return session.query(TaskModel).filter_by(name=name).count() != 0


def delete_by_id(task_id: int) -> TaskDeleteResponseEntity:
    with SessionLocal() as session:
        obj = session.query(TaskModel).filter_by(id=task_id).first()
        if not obj:
            return TaskDeleteResponseEntity.construct(ok=1, message="task not exists")
        session.delete(obj)
        session.commit()
    return TaskDeleteResponseEntity.construct(ok=0)


def toggle_start_stop(task_id: int, status: int) -> TaskToggleResponseEntity:
    with SessionLocal() as session:
        obj: TaskModel = session.query(TaskModel).filter_by(id=task_id).first()
        if not obj:
            return TaskToggleResponseEntity.construct(ok=1, message="task not exists")
        obj.status = status
        session.merge(obj)
        session.commit()
        return TaskToggleResponseEntity.construct(ok=0, data=convert_task_response_model(obj))
