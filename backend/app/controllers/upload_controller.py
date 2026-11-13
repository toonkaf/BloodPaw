import os
import re
import uuid

from fastapi import HTTPException, UploadFile, status

from app.core.config import MAX_UPLOAD_BYTES, UPLOAD_DIR

_NAME = re.compile(r"^[0-9a-f]{32}\.(jpg|png|webp)$")
MEDIA = {"jpg": "image/jpeg", "png": "image/png", "webp": "image/webp"}


def _detect(data: bytes) -> str | None:
    """ตรวจชนิดไฟล์จากเนื้อไฟล์จริง ไม่เชื่อชื่อไฟล์หรือ Content-Type ที่ผู้ใช้ส่งมา"""
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


async def save(file: UploadFile) -> str:
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "ไฟล์รูปต้องไม่เกิน 2 MB")
    ext = _detect(data)
    if ext is None:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "รองรับเฉพาะไฟล์ JPG, PNG หรือ WEBP")
    name = f"{uuid.uuid4().hex}.{ext}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(os.path.join(UPLOAD_DIR, name), "wb") as f:
        f.write(data)
    return f"/api/uploads/{name}"


def path_for(name: str) -> tuple[str, str]:
    if not _NAME.fullmatch(name):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบไฟล์")
    path = os.path.join(UPLOAD_DIR, name)
    if not os.path.isfile(path):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบไฟล์")
    return path, MEDIA[name.rsplit(".", 1)[1]]
