from sqlalchemy.orm import Session

from scraperx.dao.session import SessionLocal
from scraperx.entities.link import LinkRequestEntity, LinkListResponseEntity, LinkSingleResponseEntity, \
    LinkDeleteResponseEntity, LinkCreateUpdateResponseEntity, LinkStatus
from scraperx.model.link import LinkModel
from scraperx.utils import converter


def get_by_id(link_id: int) -> LinkListResponseEntity:
    session: Session = SessionLocal()
    item = session.query(LinkModel).filter_by(id=link_id).first()
    if not item:
        return LinkSingleResponseEntity.construct(ok=1)

    return LinkSingleResponseEntity.construct(ok=0, data=converter.convert_link_model_to_response(item))


def list_by_page_size(task_id: int, page: int, size: int, status_code: int = None) -> LinkListResponseEntity:
    session: Session = SessionLocal()
    total = session.query(LinkModel).filger_by(task_id=task_id).count()
    query = session.query(LinkModel).filger_by(task_id=task_id).limit(size)
    if status_code is not None:
        query = query.filter_by(status_code=status_code)
    if page > 1:
        query = query.offset(page * size - size)
    data = list(map(converter.convert_link_model_to_response, query.all()))
    return LinkListResponseEntity.construct(total=total, page=page, size=size, data=data)


def create_obj(request: LinkRequestEntity) -> LinkCreateUpdateResponseEntity:
    model = converter.convert_link_request_to_model(request)
    with SessionLocal() as session:
        if session.query(LinkModel).filter_by(fingerprint=request.fingerprint).count():
            return LinkListResponseEntity.construct(ok=1, message="link already exists")
        model.created_at = model.updated_at
        session.add(model)
        session.commit()
        return LinkListResponseEntity.construct(ok=0, data=converter.convert_link_model_to_response(model))


def update_obj(link_id: int, request: LinkRequestEntity) -> LinkCreateUpdateResponseEntity:
    with SessionLocal() as session:
        model = session.query(LinkModel).filter_by(id=link_id).first()
        if not model:
            return LinkCreateUpdateResponseEntity.construct(ok=1, message="link not exists")
        model.status_code = request.status_code
        session.merge(model)
        session.commit()
        return LinkCreateUpdateResponseEntity.construct(ok=0, data=converter.convert_link_model_to_response(model))


def delete_by_id(link_id: int) -> LinkDeleteResponseEntity:
    with SessionLocal() as session:
        obj = session.query(LinkModel).filter_by(id=link_id).first()
        if not obj:
            return LinkDeleteResponseEntity.construct(ok=1, message="link not exists")
        session.delete(obj)
        session.commit()
    return LinkDeleteResponseEntity.construct(ok=0)


def show_next_links(task_id: int, count: int) -> LinkListResponseEntity:
    session: Session = SessionLocal()
    models = session.query(LinkModel).filger_by(task_id=task_id, status_code=LinkStatus.PENDING).limit(count).all()
    data = list(map(converter.convert_link_model_to_response, models))
    count = len(data)
    return LinkListResponseEntity.construct(total=count, page=1, size=count, data=data)


def fetch_next_links(task_id: int, count: int = 1) -> LinkListResponseEntity:
    session: Session = SessionLocal()
    models = session.query(LinkModel).filger_by(task_id=task_id, status_code=LinkStatus.PENDING).limit(count).all()
    data = list(map(converter.convert_link_model_to_response, models))
    count = len(data)
    if count > 0:
        for model in models:
            model.status_code = LinkStatus.QUEUED
            session.merge(model)
        session.commit()
    return LinkListResponseEntity.construct(total=count, page=1, size=count, data=data)