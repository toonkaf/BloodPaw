from sqlalchemy import select
from sqlalchemy.orm import Session

from app.controllers import matching
from app.controllers.rules import case_blood_types, fail
from app.models.case import Case
from app.models.match import Match
from app.models.user import User
from app.views.case_view import CaseCreate, CaseView, OwnCaseView


def _own_view(db: Session, case: Case) -> OwnCaseView:
    v = OwnCaseView.model_validate(case)
    v.match_id = db.scalar(select(Match.id).where(Match.case_id == case.id, Match.status == "pending"))
    return v


def create(db: Session, user: User, data: CaseCreate) -> OwnCaseView:
    if data.blood_type not in case_blood_types(data.species):
        fail(["หมู่เลือดที่ต้องการไม่ถูกต้องสำหรับชนิดสัตว์นี้"])
    case = Case(owner_id=user.id, **{**data.model_dump(), "hospital": " ".join(data.hospital.split())})
    db.add(case)
    db.commit()
    matching.run_matching(db)  # พยายามจับคู่ทันที
    return _own_view(db, case)


def list_open(db: Session, hospital, species, blood_type, urgency, sort: str, limit) -> list[CaseView]:
    """เคสที่ยังไม่สำเร็จ (กำลังตามหา + พบฮีโร่)"""
    stmt = select(Case).where(Case.status != "success")
    for col, val in ((Case.hospital, hospital), (Case.species, species), (Case.blood_type, blood_type), (Case.urgency, urgency)):
        if val:
            stmt = stmt.where(col == val)
    cases = list(db.scalars(stmt.order_by(Case.created_at.desc(), Case.id.desc())))
    if sort == "urgency":
        cases.sort(key=lambda c: matching.URGENCY_RANK[c.urgency])  # sort เสถียร: ภายในระดับเดียวกันยังเรียงใหม่สุดก่อน
    return [CaseView.model_validate(c) for c in cases[:limit]]


def my_cases(db: Session, user: User) -> list[OwnCaseView]:
    cases = db.scalars(select(Case).where(Case.owner_id == user.id).order_by(Case.id.desc()))
    return [_own_view(db, c) for c in cases]
