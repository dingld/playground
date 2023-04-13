import datetime
import json
from typing import List

from scraperx.dao.session import SessionLocal
from scraperx.entities.html_parser import HtmlRuleRequestEntity, HtmlRuleListResponseEntity, \
    HtmlRuleSingleResponseEntity, HtmlRuleCreateUpdateResponseEntity, HtmlRuleDeleteResponseEntity, \
    HtmlRuleToggleResponseEntity, HtmlRuleStatus, HtmlRuleResponseEntity
from scraperx.model.html_parer import HtmlRuleModel
from scraperx.utils.converter import convert_request_to_html_rule_model, convert_model_to_html_rule_response_entity


def get_by_id(rule_id: int) -> HtmlRuleSingleResponseEntity:
    session = SessionLocal()
    item = session.query(HtmlRuleModel).filter_by(id=rule_id).first()
    if not item:
        return HtmlRuleSingleResponseEntity.construct(ok=1)

    return HtmlRuleSingleResponseEntity.construct(ok=0, data=convert_model_to_html_rule_response_entity(item))


def get_all() -> List[HtmlRuleResponseEntity]:
    session = SessionLocal()
    items = session.query(HtmlRuleModel).all()
    return list(map(convert_model_to_html_rule_response_entity, items))


def get_by_page_size(page: int, size: int):
    session = SessionLocal()
    total = session.query(HtmlRuleModel).count()
    query = session.query(HtmlRuleModel).limit(size)
    if page > 1:
        query = query.offset(page * size - size)
    data = list(map(convert_model_to_html_rule_response_entity, query.all()))
    return HtmlRuleListResponseEntity.construct(total=total, page=page, size=size, data=data)


def create_obj(request: HtmlRuleRequestEntity):
    with SessionLocal() as session:
        model = convert_request_to_html_rule_model(request)
        if exist_by_name(session, model.name):
            return HtmlRuleCreateUpdateResponseEntity.construct(ok=1, message="rule already exists")
        model.created_at = model.updated_at
        session.add(model)
        session.commit()
        return HtmlRuleCreateUpdateResponseEntity.construct(ok=0,
                                                            data=convert_model_to_html_rule_response_entity(model))


def update_obj(rule_id: int, request: HtmlRuleRequestEntity):
    with SessionLocal() as session:
        convert_request_to_html_rule_model(request)

        model: HtmlRuleModel = session.query(HtmlRuleModel).filter_by(id=rule_id).first()
        if not model:
            return HtmlRuleCreateUpdateResponseEntity.construct(ok=1, message="rule not exists")
        if model.name != request.name:
            if exist_by_name(session, request.name):
                return HtmlRuleCreateUpdateResponseEntity.construct(ok=1, message="rule name dupelicated")
        model.name = request.name
        model.domain = request.domain
        model.path = request.path
        model.type = request.type
        model.rules = json.dumps(request.rules)
        model.updated_at = datetime.datetime.now()
        session.merge(model)
        session.commit()
        return HtmlRuleCreateUpdateResponseEntity.construct(ok=0,
                                                            data=convert_model_to_html_rule_response_entity(model))


def exist_by_name(session: SessionLocal, name: str):
    return session.query(HtmlRuleModel).filter_by(name=name).count() != 0


def delete_by_id(rule_id: int):
    with SessionLocal() as session:
        obj = session.query(HtmlRuleModel).filter_by(id=rule_id).first()
        if not obj:
            return HtmlRuleDeleteResponseEntity.construct(ok=1, message="rule not exists")
        session.delete(obj)
        session.commit()
        return HtmlRuleDeleteResponseEntity.construct(ok=0)


def toggle_start_stop(rule_id: int, status: int):
    with SessionLocal() as session:
        if not HtmlRuleStatus.is_legal(status):
            return HtmlRuleToggleResponseEntity.construct(ok=1, message="ilegal status")

        obj: HtmlRuleModel = session.query(HtmlRuleModel).filter_by(id=rule_id).first()
        if not obj:
            return HtmlRuleToggleResponseEntity.construct(ok=1, message="rule not exists")
        obj.status = status
        session.merge(obj)
        session.commit()
        return HtmlRuleToggleResponseEntity.construct(ok=0, data=convert_model_to_html_rule_response_entity(obj))
