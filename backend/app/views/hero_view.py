from pydantic import BaseModel, ConfigDict, Field

from app.views.common import Phone, Species


class HeroCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    species: Species
    blood_type: str = Field(min_length=1, max_length=20)
    weight_kg: float = Field(gt=0, lt=100)
    province: str = Field(min_length=1, max_length=60)
    contact_phone: str = Field(pattern=Phone)


class HeroAvailability(BaseModel):
    available: bool


class HeroView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    species: str
    blood_type: str
    weight_kg: float
    province: str
    available: bool
    contact_phone: str | None = None   # เห็นเฉพาะผู้ที่เข้าสู่ระบบ
