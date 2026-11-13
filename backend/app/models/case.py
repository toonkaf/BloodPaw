from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Case(Base):
    """เคสด่วน = ประกาศหาเลือดให้สัตว์ป่วย"""
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    pet_name: Mapped[str] = mapped_column(String(80))
    species: Mapped[str] = mapped_column(String(10))            # dog | cat
    breed: Mapped[str] = mapped_column(String(80))
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    symptom: Mapped[str] = mapped_column(String(200))
    cause: Mapped[str] = mapped_column(String(200))
    photo_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    blood_type: Mapped[str] = mapped_column(String(20))         # หมู่เลือดที่ต้องการ หรือ "ไม่ระบุ"
    min_donor_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    hospital: Mapped[str] = mapped_column(String(120))
    vet_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    contact_phone: Mapped[str] = mapped_column(String(20))      # ส่วนตัว: ส่งผ่านปุ่ม tel ในแชทเท่านั้น
    urgency: Mapped[str] = mapped_column(String(10), default="urgent")   # advance | urgent | critical
    status: Mapped[str] = mapped_column(String(10), default="searching", index=True)  # searching | found | success
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
