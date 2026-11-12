from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.controllers import auth_controller, case_controller, health_controller, hero_controller, stats_controller
from app.core.database import get_db
from app.core.security import get_current_user, get_optional_user
from app.models.user import User
from app.views.case_view import CaseCreate, CaseView
from app.views.hero_view import HeroAvailability, HeroCreate, HeroView
from app.views.stats_view import StatsView
from app.views.user_view import LoginRequest, RegisterRequest, TokenView, UserView

router = APIRouter(prefix="/api")


@router.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        return health_controller.check(db)
    except Exception:
        raise HTTPException(503, "database unavailable")


# ---- Auth ----
@router.post("/auth/register", response_model=UserView, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return auth_controller.register(db, data)


@router.post("/auth/login", response_model=TokenView)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return TokenView(access_token=auth_controller.login(db, data))


@router.get("/me", response_model=UserView)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/me/cases", response_model=list[CaseView])
def my_cases(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return case_controller.my_cases(db, user)


@router.get("/me/heroes", response_model=list[HeroView])
def my_heroes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return hero_controller.my_heroes(db, user)


# ---- Dashboard ----
@router.get("/stats", response_model=StatsView)
def stats(db: Session = Depends(get_db)):
    return stats_controller.get_stats(db)


# ---- Cases (เคสด่วน) ----
@router.get("/cases", response_model=list[CaseView])
def list_cases(
    status: Literal["searching", "closed"] | None = None,
    species: Literal["dog", "cat"] | None = None,
    province: str | None = None,
    limit: int | None = Query(default=None, ge=1, le=100),
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_optional_user),
):
    return case_controller.list_cases(db, viewer, status, species, province, limit)


@router.post("/cases", response_model=CaseView, status_code=201)
def create_case(data: CaseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return case_controller.create(db, user, data)


@router.post("/cases/{case_id}/close", response_model=CaseView)
def close_case(case_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return case_controller.close(db, user, case_id)


# ---- Heroes (ฮีโร่) ----
@router.get("/heroes", response_model=list[HeroView])
def list_heroes(
    species: Literal["dog", "cat"] | None = None,
    province: str | None = None,
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_optional_user),
):
    return hero_controller.list_heroes(db, viewer, species, province)


@router.post("/heroes", response_model=HeroView, status_code=201)
def register_hero(data: HeroCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return hero_controller.register(db, user, data)


@router.patch("/heroes/{hero_id}", response_model=HeroView)
def set_hero_availability(hero_id: int, data: HeroAvailability, db: Session = Depends(get_db),
                          user: User = Depends(get_current_user)):
    return hero_controller.set_availability(db, user, hero_id, data.available)
