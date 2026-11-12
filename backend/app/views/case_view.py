from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.views.common import Phone, Species


class CaseCreate(BaseModel):
    pet_name: str = Field(min_length=1, max_length=80)
    species: Species
    blood_type: str = Field(min_length=1, max_length=20)
    hospital: str = Field(min_length=1, max_length=120)
    province: str = Field(min_length=1, max_length=60)
    urgency: Literal["normal", "urgent", "critical"] = "urgent"
    contact_phone: str = Field(pattern=Phone)
    note: str = Field(default="", max_length=500)


class CaseView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    pet_name: str
    species: str
    blood_type: str
    hospital: str
    province: str
    urgency: str
    note: str
    status: str
    created_at: datetime
    contact_phone: str | None = None   # เห็นเฉพาะผู้ที่เข้าสู่ระบบ
