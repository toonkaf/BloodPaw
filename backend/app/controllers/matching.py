"""ระบบจับคู่เคสด่วนกับฮีโร่อัตโนมัติ

เงื่อนไขที่ฮีโร่ต้องผ่านทั้งหมด: พร้อม (ไม่พัก) / ชนิดเดียวกัน / ไม่ใช่สัตว์ของเจ้าของเคสเอง /
หมู่เลือดเข้ากัน / น้ำหนักถึงเกณฑ์ / สะดวกบริจาคที่โรงพยาบาลของเคส / ไม่ได้ถูกปฏิเสธเคสนี้มาก่อน /
ไม่ได้ถือคำขออื่นที่ยังรอตัดสินใจอยู่ (ฮีโร่ 1 ตัวรับได้ทีละ 1 เคส)
ลำดับ: เคส "ด่วนมาก" ก่อน แล้วตามเวลาที่ประกาศ; ฮีโร่ที่หมู่เลือดตรงเป๊ะก่อนฮีโร่ที่ไม่ทราบหมู่เลือด
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.controllers.rules import MIN_DONOR_WEIGHT_KG, UNKNOWN, UNSPECIFIED
from app.models.case import Case
from app.models.hero import Hero
from app.models.match import Match

URGENCY_RANK = {"critical": 0, "urgent": 1, "advance": 2}


def _norm(s: str) -> str:
    return " ".join(s.split()).casefold()


def hero_fits_case(hero: Hero, case: Case) -> bool:
    if hero.status != "ready" or hero.species != case.species or hero.owner_id == case.owner_id:
        return False
    if not (case.blood_type == UNSPECIFIED or hero.blood_type == UNKNOWN or case.blood_type == hero.blood_type):
        return False
    if hero.weight_kg < (case.min_donor_weight or MIN_DONOR_WEIGHT_KG[case.species]):
        return False
    return _norm(case.hospital) in {_norm(h) for h in hero.hospitals}


def cancel_pending(db: Session, *, hero_id: int | None = None, match: Match | None = None) -> None:
    """ยกเลิกคำขอที่รออยู่ แล้วคืนเคสไปสถานะ 'กำลังตามหา'"""
    matches = [match] if match else list(db.scalars(select(Match).where(Match.hero_id == hero_id, Match.status == "pending")))
    for m in matches:
        m.status = "cancelled"
        case = db.get(Case, m.case_id)
        if case and case.status == "found":
            case.status = "searching"


def run_matching(db: Session) -> None:
    db.flush()
    cases = sorted(db.scalars(select(Case).where(Case.status == "searching")),
                   key=lambda c: (URGENCY_RANK[c.urgency], c.created_at, c.id))
    heroes = list(db.scalars(select(Hero).where(Hero.status == "ready").order_by(Hero.id)))
    busy = set(db.scalars(select(Match.hero_id).where(Match.status == "pending")))
    declined = {(r[0], r[1]) for r in db.execute(select(Match.case_id, Match.hero_id).where(Match.status == "declined"))}

    for case in cases:
        candidates = [h for h in heroes if h.id not in busy and (case.id, h.id) not in declined and hero_fits_case(h, case)]
        if not candidates:
            continue
        hero = min(candidates, key=lambda h: (0 if h.blood_type == case.blood_type else 1, h.id))
        db.add(Match(case_id=case.id, hero_id=hero.id, status="pending"))
        case.status = "found"
        busy.add(hero.id)
    db.commit()
