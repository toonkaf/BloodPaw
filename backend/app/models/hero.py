from datetime import date

from sqlalchemy import JSON, Boolean, Date, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Hero(Base):
    """ฮีโร่ = สัตว์เลี้ยงที่ลงทะเบียนพร้อมบริจาคเลือด"""
    __tablename__ = "heroes"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    species: Mapped[str] = mapped_column(String(10))            # dog | cat
    breed: Mapped[str] = mapped_column(String(80))
    birth_date: Mapped[date] = mapped_column(Date)
    weight_kg: Mapped[float] = mapped_column(Float)
    blood_type: Mapped[str] = mapped_column(String(20))
    vaccinated_ok: Mapped[bool] = mapped_column(Boolean)
    no_chronic_disease: Mapped[bool] = mapped_column(Boolean)
    hospitals: Mapped[list] = mapped_column(JSON)               # โรงพยาบาลที่สะดวกบริจาค (หลายแห่ง)
    province: Mapped[str] = mapped_column(String(60))
    contact_phone: Mapped[str] = mapped_column(String(20))      # ส่วนตัว: ส่งผ่านปุ่ม tel ในแชทเท่านั้น
    photo_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(10), default="ready", index=True)  # ready | resting
