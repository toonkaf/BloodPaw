from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.views.common import PHONE, PHOTO, Species


class HeroCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    species: Species
    breed: str = Field(min_length=1, max_length=80)
    birth_date: date
    weight_kg: float = Field(gt=0, lt=150)
    photo_url: str | None = Field(default=None, pattern=PHOTO)
    blood_type: str = Field(min_length=1, max_length=20)
    vaccinated_ok: bool
    no_chronic_disease: bool
    criteria_confirmed: bool
    hospitals: list[str] = Field(min_length=1, max_length=10)
    province: str = Field(min_length=1, max_length=60)
    contact_phone: str = Field(pattern=PHONE)


class HeroStatusUpdate(BaseModel):
    status: Literal["ready", "resting"]


class HeroView(BaseModel):
    """มุมมองสาธารณะ/ของคู่สนทนา — ไม่มีเบอร์โทร"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    species: str
    breed: str
    birth_date: date
    weight_kg: float
    blood_type: str
    hospitals: list[str]
    province: str
    photo_url: str | None = None
    status: str


class HeroOwnView(HeroView):
    """มุมมองเจ้าของ (ใช้เติมฟอร์มแก้ไข)"""
    vaccinated_ok: bool
    no_chronic_disease: bool
    contact_phone: str
