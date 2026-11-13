from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import app.models  # noqa: F401  (ลงทะเบียน Model ก่อน create_all)
from app.core.database import Base, engine
from app.routes.api import router

FIELD_LABELS = {
    "full_name": "ชื่อ", "email": "อีเมล", "password": "รหัสผ่าน", "name": "ชื่อ", "species": "ชนิด", "breed": "สายพันธุ์",
    "birth_date": "วันเกิด", "weight_kg": "น้ำหนัก", "blood_type": "กรุ๊ปเลือด", "hospitals": "โรงพยาบาล",
    "hospital": "โรงพยาบาล", "province": "จังหวัด", "contact_phone": "เบอร์โทร (ขึ้นต้น 0 และมี 9-10 หลัก)",
    "pet_name": "ชื่อสัตว์ป่วย", "symptom": "อาการ", "cause": "สาเหตุ", "urgency": "ระดับความเร่งด่วน",
    "photo_url": "รูปภาพ", "min_donor_weight": "น้ำหนักขั้นต่ำ", "vaccinated_ok": "วัคซีน",
    "no_chronic_disease": "โรคประจำตัว", "criteria_confirmed": "การยืนยันเกณฑ์", "body": "ข้อความ", "vet_name": "ชื่อสัตวแพทย์",
}


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Mini Project: ใช้ create_all; งานจริงควรใช้ Alembic migration
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="PetTech API", lifespan=lifespan)
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError):
    """แปลงข้อผิดพลาดของ Pydantic เป็นข้อความไทย 'ช่องไหนลืมกรอก/ผิดรูปแบบ'"""
    errors = []
    for e in exc.errors():
        loc = [str(x) for x in e["loc"] if x not in ("body", "query", "path")]
        label = FIELD_LABELS.get(loc[0] if loc else "", loc[0] if loc else "ข้อมูล")
        msg = f"{label}: กรอกไม่ครบหรือรูปแบบไม่ถูกต้อง"
        if msg not in errors:
            errors.append(msg)
    return JSONResponse(status_code=422, content={"detail": {"errors": errors}})
