from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.views.case_view import CaseView
from app.views.hero_view import HeroView


class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=1000)

    @field_validator("body")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("blank")
        return v


class MessageView(BaseModel):
    id: int
    kind: str          # text | tel
    body: str
    created_at: datetime
    mine: bool


class MatchDetail(BaseModel):
    id: int
    status: str        # pending | declined | cancelled | confirmed
    role: str          # hero_owner | case_owner
    case: CaseView
    hero: HeroView
    messages: list[MessageView]


class RequestView(BaseModel):
    match_id: int
    case: CaseView
