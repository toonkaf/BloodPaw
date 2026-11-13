from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.controllers import matching
from app.models.case import Case
from app.models.hero import Hero
from app.models.match import Match, Message
from app.models.user import User
from app.views.case_view import CaseView
from app.views.hero_view import HeroView
from app.views.match_view import MatchDetail, MessageView, RequestView


def _load(db: Session, user: User, match_id: int):
    """คืน (match, case, hero, role) เฉพาะผู้ที่เกี่ยวข้อง; คนอื่นได้ 404 เหมือนไม่มีอยู่จริง"""
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบการติดต่อ")
    case, hero = db.get(Case, match.case_id), db.get(Hero, match.hero_id)
    if case.owner_id == user.id:
        role = "case_owner"
    elif hero.owner_id == user.id:
        role = "hero_owner"
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบการติดต่อ")
    return match, case, hero, role


def _require_pending(match: Match) -> None:
    if match.status != "pending":
        raise HTTPException(status.HTTP_409_CONFLICT, "การติดต่อนี้สิ้นสุดแล้ว")


def detail(db: Session, user: User, match_id: int) -> MatchDetail:
    match, case, hero, role = _load(db, user, match_id)
    msgs = db.scalars(select(Message).where(Message.match_id == match.id).order_by(Message.id))
    return MatchDetail(
        id=match.id, status=match.status, role=role,
        case=CaseView.model_validate(case), hero=HeroView.model_validate(hero),
        messages=[MessageView(id=m.id, kind=m.kind, body=m.body, created_at=m.created_at, mine=m.sender_id == user.id) for m in msgs],
    )


def _post(db: Session, user: User, match: Match, kind: str, body: str) -> Message:
    msg = Message(match_id=match.id, sender_id=user.id, kind=kind, body=body)
    db.add(msg)
    db.commit()
    return msg


def send_message(db: Session, user: User, match_id: int, body: str) -> MessageView:
    match, _, _, _ = _load(db, user, match_id)
    _require_pending(match)
    m = _post(db, user, match, "text", body)
    return MessageView(id=m.id, kind=m.kind, body=m.body, created_at=m.created_at, mine=True)


def share_phone(db: Session, user: User, match_id: int) -> MessageView:
    """ปุ่ม tel: ส่งเบอร์ที่เจ้าของกรอกไว้ตอนลงทะเบียนฮีโร่/ประกาศเคส ให้อีกฝ่ายทันที"""
    match, case, hero, role = _load(db, user, match_id)
    _require_pending(match)
    m = _post(db, user, match, "tel", case.contact_phone if role == "case_owner" else hero.contact_phone)
    return MessageView(id=m.id, kind=m.kind, body=m.body, created_at=m.created_at, mine=True)


def decline(db: Session, user: User, match_id: int) -> dict:
    match, case, _, _ = _load(db, user, match_id)
    _require_pending(match)
    match.status = "declined"       # คู่นี้จะไม่ถูกจับซ้ำกับเคสนี้
    case.status = "searching"
    db.commit()
    matching.run_matching(db)       # จับคู่ใหม่ให้เคสทันที
    return {"status": "declined"}


def confirm(db: Session, user: User, match_id: int) -> dict:
    match, case, _, _ = _load(db, user, match_id)
    _require_pending(match)
    match.status = "confirmed"
    case.status = "success"
    db.commit()
    return {"status": "confirmed"}


def my_requests(db: Session, user: User) -> list[RequestView]:
    """คำขอที่ได้รับ = คู่ที่ระบบจับให้ฮีโร่ของเรา และยังรอการตัดสินใจ"""
    stmt = (select(Match, Case).join(Hero, Hero.id == Match.hero_id).join(Case, Case.id == Match.case_id)
            .where(Hero.owner_id == user.id, Match.status == "pending").order_by(Match.id.desc()))
    return [RequestView(match_id=m.id, case=CaseView.model_validate(c)) for m, c in db.execute(stmt).all()]
