from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Hero(Base):
    """ฮีโร่ = สัตว์เลี้ยงที่ลงทะเบียนพร้อมบริจาคเลือด"""
    __tablename__ = "heroes"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    species: Mapped[str] = mapped_column(String(10))       # dog | cat
    blood_type: Mapped[str] = mapped_column(String(20))
    weight_kg: Mapped[float] = mapped_column(Float)
    province: Mapped[str] = mapped_column(String(60), index=True)
    contact_phone: Mapped[str] = mapped_column(String(20))
    available: Mapped[bool] = mapped_column(Boolean, default=True)
