from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_token, hash_password, verify_password
from app.models.user import User
from app.views.user_view import LoginRequest, RegisterRequest


def register(db: Session, data: RegisterRequest) -> User:
    if db.scalar(select(User).where(User.email == data.email.lower())):
        raise HTTPException(status.HTTP_409_CONFLICT, "อีเมลนี้ถูกใช้แล้ว")
    user = User(
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    db.commit()
    return user


def login(db: Session, data: LoginRequest) -> str:
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    # ข้อความเดียวกันทุกกรณี ไม่เปิดเผยว่าผิดช่องใด
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "อีเมลหรือรหัสผ่านไม่ถูกต้อง")
    return create_token(user.id)
