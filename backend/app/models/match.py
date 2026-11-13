from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Match(Base):
    """การจับคู่ เคสด่วน <-> ฮีโร่ (ระบบสร้างให้อัตโนมัติ)"""
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    hero_id: Mapped[int] = mapped_column(ForeignKey("heroes.id"), index=True)
    # pending = รอการตัดสินใจ | declined = ถูกปฏิเสธ | cancelled = ฮีโร่พัก/ข้อมูลไม่เข้าเกณฑ์ | confirmed = สำเร็จ
    status: Mapped[str] = mapped_column(String(12), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    kind: Mapped[str] = mapped_column(String(8), default="text")   # text | tel
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
