from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.controllers.blood_rules import MIN_DONOR_WEIGHT_KG, check_blood_type
from app.models.hero import Hero
from app.models.user import User
from app.views.hero_view import HeroCreate, HeroView


def _view(hero: Hero, viewer: User | None) -> HeroView:
    v = HeroView.model_validate(hero)
    v.contact_phone = hero.contact_phone if viewer else None  # Privacy: ซ่อนเบอร์จากผู้ไม่ได้ล็อกอิน
    return v


def register(db: Session, user: User, data: HeroCreate) -> HeroView:
    check_blood_type(data.species, data.blood_type)
    if data.weight_kg < MIN_DONOR_WEIGHT_KG[data.species]:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"น้ำหนักต้องไม่ต่ำกว่า {MIN_DONOR_WEIGHT_KG[data.species]:g} กก. จึงจะเป็นผู้บริจาคได้",
        )
    hero = Hero(owner_id=user.id, **data.model_dump())
    db.add(hero)
    db.commit()
    return _view(hero, user)


def list_heroes(db: Session, viewer: User | None, species: str | None, province: str | None) -> list[HeroView]:
    stmt = select(Hero).where(Hero.available.is_(True)).order_by(Hero.id.desc())
    if species:
        stmt = stmt.where(Hero.species == species)
    if province:
        stmt = stmt.where(Hero.province == province)
    return [_view(h, viewer) for h in db.scalars(stmt)]


def my_heroes(db: Session, user: User) -> list[HeroView]:
    return [_view(h, user) for h in db.scalars(select(Hero).where(Hero.owner_id == user.id).order_by(Hero.id.desc()))]


def set_availability(db: Session, user: User, hero_id: int, available: bool) -> HeroView:
    hero = db.get(Hero, hero_id)
    if hero is None or hero.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบฮีโร่")
    hero.available = available
    db.commit()
    return _view(hero, user)
