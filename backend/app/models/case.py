from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Case(Base):
    """เคสด่วน = ประกาศหาเลือดให้สัตว์ป่วย"""
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    pet_name: Mapped[str] = mapped_column(String(80))
    species: Mapped[str] = mapped_column(String(10))       # dog | cat
    blood_type: Mapped[str] = mapped_column(String(20))
    hospital: Mapped[str] = mapped_column(String(120))
    province: Mapped[str] = mapped_column(String(60), index=True)
    urgency: Mapped[str] = mapped_column(String(10), default="urgent")   # normal | urgent | critical
    contact_phone: Mapped[str] = mapped_column(String(20))
    note: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(10), default="searching", index=True)  # searching | closed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
