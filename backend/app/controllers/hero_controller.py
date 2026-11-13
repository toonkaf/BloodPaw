from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.controllers import matching
from app.controllers.rules import AGE_RANGE_YEARS, BLOOD_TYPES, MIN_DONOR_WEIGHT_KG, age_years, fail
from app.models.case import Case
from app.models.hero import Hero
from app.models.match import Match
from app.models.user import User
from app.views.hero_view import HeroCreate, HeroOwnView

_EDITABLE = ["name", "species", "breed", "birth_date", "weight_kg", "photo_url", "blood_type",
             "vaccinated_ok", "no_chronic_disease", "hospitals", "province", "contact_phone"]


def _check(data: HeroCreate) -> list[str]:
    """ตรวจเกณฑ์ผู้บริจาค คืนรายการสิ่งที่ไม่ผ่านทั้งหมด"""
    errs = []
    if data.blood_type not in BLOOD_TYPES[data.species]:
        errs.append("หมู่เลือดไม่ถูกต้องสำหรับชนิดสัตว์นี้")
    lo, hi = AGE_RANGE_YEARS[data.species]
    if data.birth_date > date.today():
        errs.append("วันเกิดต้องไม่อยู่ในอนาคต")
    elif not lo <= age_years(data.birth_date) <= hi:
        errs.append(f"อายุต้องอยู่ระหว่าง {lo}-{hi} ปี (ปัจจุบัน {age_years(data.birth_date)} ปี)")
    if data.weight_kg < MIN_DONOR_WEIGHT_KG[data.species]:
        errs.append(f"น้ำหนักต้องไม่ต่ำกว่า {MIN_DONOR_WEIGHT_KG[data.species]:g} กก.")
    if not data.vaccinated_ok:
        errs.append("ต้องได้รับวัคซีนพื้นฐานครบ และยังไม่หมดอายุ")
    if not data.no_chronic_disease:
        errs.append("ต้องไม่มีโรคประจำตัวเรื้อรัง")
    if not data.criteria_confirmed:
        errs.append("กรุณายืนยันว่าอ่านเกณฑ์แล้วและน้องฮีโร่ผ่านเกณฑ์")
    return errs


def _clean_hospitals(hospitals: list[str]) -> list[str]:
    seen, out = set(), []
    for h in hospitals:
        h = " ".join(h.split())
        if h and h.casefold() not in seen:
            seen.add(h.casefold())
            out.append(h)
    return out


def _owned(db: Session, user: User, hero_id: int) -> Hero:
    hero = db.get(Hero, hero_id)
    if hero is None or hero.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบฮีโร่")
    return hero


def register(db: Session, user: User, data: HeroCreate) -> Hero:
    errs = _check(data)
    hospitals = _clean_hospitals(data.hospitals)
    if not hospitals:
        errs.append("กรุณาระบุโรงพยาบาลที่สะดวกบริจาคอย่างน้อย 1 แห่ง")
    if errs:
        fail(errs)
    values = data.model_dump(exclude={"criteria_confirmed", "hospitals"})
    hero = Hero(owner_id=user.id, hospitals=hospitals, status="ready", **values)
    db.add(hero)
    db.commit()
    matching.run_matching(db)
    return hero


def update(db: Session, user: User, hero_id: int, data: HeroCreate) -> Hero:
    hero = _owned(db, user, hero_id)
    errs = _check(data)
    hospitals = _clean_hospitals(data.hospitals)
    if not hospitals:
        errs.append("กรุณาระบุโรงพยาบาลที่สะดวกบริจาคอย่างน้อย 1 แห่ง")
    if errs:
        fail(errs)
    for f in _EDITABLE:
        setattr(hero, f, hospitals if f == "hospitals" else getattr(data, f))
    # คำขอที่รออยู่ แต่ข้อมูลใหม่ไม่เข้าเงื่อนไขแล้ว -> ยกเลิกและหาฮีโร่ใหม่ให้เคสนั้น
    for m in list(db.scalars(select(Match).where(Match.hero_id == hero.id, Match.status == "pending"))):
        case = db.get(Case, m.case_id)
        if not matching.hero_fits_case(hero, case):
            matching.cancel_pending(db, match=m)
    db.commit()
    matching.run_matching(db)
    return hero


def set_status(db: Session, user: User, hero_id: int, new_status: str) -> Hero:
    hero = _owned(db, user, hero_id)
    hero.status = new_status
    if new_status == "resting":  # พัก: ยกเลิกคำขอที่ถือไว้ ให้ระบบจับเคสนั้นกับฮีโร่ตัวอื่น
        matching.cancel_pending(db, hero_id=hero.id)
    db.commit()
    matching.run_matching(db)
    return hero


def my_heroes(db: Session, user: User) -> list[HeroOwnView]:
    heroes = db.scalars(select(Hero).where(Hero.owner_id == user.id).order_by(Hero.id.desc()))
    return [HeroOwnView.model_validate(h) for h in heroes]
