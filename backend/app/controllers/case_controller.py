from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.controllers.blood_rules import check_blood_type
from app.models.case import Case
from app.models.user import User
from app.views.case_view import CaseCreate, CaseView

_URGENCY_ORDER = {"critical": 0, "urgent": 1, "normal": 2}


def _view(case: Case, viewer: User | None) -> CaseView:
    v = CaseView.model_validate(case)
    v.contact_phone = case.contact_phone if viewer else None  # Privacy: ซ่อนเบอร์จากผู้ไม่ได้ล็อกอิน
    return v


def create(db: Session, user: User, data: CaseCreate) -> CaseView:
    check_blood_type(data.species, data.blood_type)
    case = Case(owner_id=user.id, **data.model_dump())
    db.add(case)
    db.commit()
    return _view(case, user)


def list_cases(db: Session, viewer: User | None, status_: str | None, species: str | None,
               province: str | None, limit: int | None) -> list[CaseView]:
    stmt = select(Case).order_by(Case.created_at.desc(), Case.id.desc())
    if status_:
        stmt = stmt.where(Case.status == status_)
    if species:
        stmt = stmt.where(Case.species == species)
    if province:
        stmt = stmt.where(Case.province == province)
    cases = list(db.scalars(stmt))
    if status_ == "searching" or status_ is None:  # เคสวิกฤตขึ้นก่อน
        cases.sort(key=lambda c: (c.status != "searching", _URGENCY_ORDER[c.urgency]))
    return [_view(c, viewer) for c in cases[:limit]]


def my_cases(db: Session, user: User) -> list[CaseView]:
    return [_view(c, user) for c in db.scalars(select(Case).where(Case.owner_id == user.id).order_by(Case.id.desc()))]


def close(db: Session, user: User, case_id: int) -> CaseView:
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบเคส")
    if case.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "เฉพาะเจ้าของเคสเท่านั้นที่ปิดเคสได้")
    if case.status == "closed":
        raise HTTPException(status.HTTP_409_CONFLICT, "เคสนี้ปิดไปแล้ว")
    case.status = "closed"
    db.commit()
    return _view(case, user)
