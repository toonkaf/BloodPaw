from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.views.common import PHONE, PHOTO, Species, Urgency


class CaseCreate(BaseModel):
    species: Species
    pet_name: str = Field(min_length=1, max_length=80)
    breed: str = Field(min_length=1, max_length=80)
    birth_date: date | None = None
    weight_kg: float | None = Field(default=None, gt=0, lt=150)
    symptom: str = Field(min_length=1, max_length=200)
    cause: str = Field(min_length=1, max_length=200)
    photo_url: str | None = Field(default=None, pattern=PHOTO)
    blood_type: str = Field(min_length=1, max_length=20)
    min_donor_weight: float | None = Field(default=None, gt=0, lt=150)
    hospital: str = Field(min_length=1, max_length=120)
    vet_name: str | None = Field(default=None, max_length=80)
    contact_phone: str = Field(pattern=PHONE)
    urgency: Urgency


class CaseView(BaseModel):
    """มุมมองสาธารณะ — ไม่มีเบอร์โทร"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    species: str
    pet_name: str
    breed: str
    birth_date: date | None = None
    weight_kg: float | None = None
    symptom: str
    cause: str
    photo_url: str | None = None
    blood_type: str
    min_donor_weight: float | None = None
    hospital: str
    vet_name: str | None = None
    urgency: str
    status: str
    created_at: datetime


class OwnCaseView(CaseView):
    match_id: int | None = None   # มีค่าเมื่อระบบจับคู่ฮีโร่ได้และยังรอการตัดสินใจ
