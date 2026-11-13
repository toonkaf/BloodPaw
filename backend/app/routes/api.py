from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.controllers import (auth_controller, case_controller, health_controller, hero_controller, match_controller,
                             stats_controller, upload_controller)
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.views.case_view import CaseCreate, CaseView, OwnCaseView
from app.views.common import Species, Urgency
from app.views.hero_view import HeroCreate, HeroOwnView, HeroStatusUpdate
from app.views.match_view import MatchDetail, MessageCreate, MessageView, RequestView
from app.views.stats_view import MetaView, StatsView
from app.views.user_view import LoginRequest, RegisterRequest, TokenView, UserView

router = APIRouter(prefix="/api")


@router.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        return health_controller.check(db)
    except Exception:
        raise HTTPException(503, "database unavailable")


# ---- Auth / Profile ----
@router.post("/auth/register", response_model=UserView, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return auth_controller.register(db, data)


@router.post("/auth/login", response_model=TokenView)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return TokenView(access_token=auth_controller.login(db, data))


@router.get("/me", response_model=UserView)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/me/heroes", response_model=list[HeroOwnView])
def my_heroes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return hero_controller.my_heroes(db, user)


@router.get("/me/cases", response_model=list[OwnCaseView])
def my_cases(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return case_controller.my_cases(db, user)


@router.get("/me/requests", response_model=list[RequestView])
def my_requests(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return match_controller.my_requests(db, user)


# ---- Public ----
@router.get("/stats", response_model=StatsView)
def stats(db: Session = Depends(get_db)):
    return stats_controller.get_stats(db)


@router.get("/meta", response_model=MetaView)
def meta(db: Session = Depends(get_db)):
    return stats_controller.get_meta(db)


@router.get("/cases", response_model=list[CaseView])
def list_cases(
    hospital: str | None = None,
    species: Species | None = None,
    blood_type: str | None = None,
    urgency: Urgency | None = None,
    sort: Literal["urgency", "latest"] = "urgency",
    limit: int | None = Query(default=None, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return case_controller.list_open(db, hospital, species, blood_type, urgency, sort, limit)


@router.get("/uploads/{name}")
def get_upload(name: str):
    path, media = upload_controller.path_for(name)
    return FileResponse(path, media_type=media,
                        headers={"Cache-Control": "public, max-age=31536000, immutable", "X-Content-Type-Options": "nosniff"})


# ---- Need login ----
@router.post("/uploads", status_code=201)
async def upload(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    return {"url": await upload_controller.save(file)}


@router.post("/cases", response_model=OwnCaseView, status_code=201)
def create_case(data: CaseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return case_controller.create(db, user, data)


@router.post("/heroes", response_model=HeroOwnView, status_code=201)
def register_hero(data: HeroCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return hero_controller.register(db, user, data)


@router.put("/heroes/{hero_id}", response_model=HeroOwnView)
def update_hero(hero_id: int, data: HeroCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return hero_controller.update(db, user, hero_id, data)


@router.patch("/heroes/{hero_id}/status", response_model=HeroOwnView)
def set_hero_status(hero_id: int, data: HeroStatusUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return hero_controller.set_status(db, user, hero_id, data.status)


# ---- Match: หน้าติดต่อ (แชท) / ปฏิเสธ / ยืนยัน ----
@router.get("/matches/{match_id}", response_model=MatchDetail)
def match_detail(match_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return match_controller.detail(db, user, match_id)


@router.post("/matches/{match_id}/messages", response_model=MessageView, status_code=201)
def send_message(match_id: int, data: MessageCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return match_controller.send_message(db, user, match_id, data.body)


@router.post("/matches/{match_id}/share-phone", response_model=MessageView, status_code=201)
def share_phone(match_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return match_controller.share_phone(db, user, match_id)


@router.post("/matches/{match_id}/decline")
def decline(match_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return match_controller.decline(db, user, match_id)


@router.post("/matches/{match_id}/confirm")
def confirm(match_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return match_controller.confirm(db, user, match_id)
