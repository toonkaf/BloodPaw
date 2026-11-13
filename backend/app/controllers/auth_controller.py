from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.controllers.rules import fail
from app.core.security import create_token, hash_password, verify_password
from app.models.user import User
from app.views.user_view import LoginRequest, RegisterRequest


def _norm(s: str) -> str:
    return " ".join(s.split()).casefold()


def register(db: Session, data: RegisterRequest) -> User:
    errors = []
    if len(data.password) < 8:
        errors.append("รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร")
    if not (any(c.isalpha() for c in data.password) and any(c.isdigit() for c in data.password)):
        errors.append("รหัสผ่านต้องมีทั้งตัวอักษรและตัวเลข")
    if errors:
        fail(errors)
    if db.scalar(select(User).where(User.email == data.email.lower())):
        raise HTTPException(status.HTTP_409_CONFLICT, "อีเมลนี้ถูกใช้แล้ว")
    user = User(email=data.email.lower(), password_hash=hash_password(data.password), full_name=data.full_name.strip())
    db.add(user)
    db.commit()
    return user


def login(db: Session, data: LoginRequest) -> str:
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    ok = user is not None and verify_password(data.password, user.password_hash) and _norm(data.full_name) == _norm(user.full_name)
    if not ok:  # ข้อความเดียวกันทุกกรณี ไม่เปิดเผยว่าผิดช่องใด
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "อีเมลหรือรหัสผ่านไม่ถูกต้อง")
    return create_token(user.id)
