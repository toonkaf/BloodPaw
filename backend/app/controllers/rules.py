"""กฎของระบบรวมไว้ที่เดียว (ทีมควรตรวจกับสัตวแพทย์/แหล่งอ้างอิงก่อนใช้จริง)"""
from datetime import date

from fastapi import HTTPException, status

UNKNOWN = "ไม่ทราบ"        # ฮีโร่ไม่ทราบหมู่เลือด -> สัตวแพทย์ตรวจก่อนบริจาค
UNSPECIFIED = "ไม่ระบุ"    # เคสไม่ระบุหมู่เลือด

BLOOD_TYPES = {
    "dog": ["DEA 1.1+", "DEA 1.1-", "DEA 1.2", UNKNOWN],
    "cat": ["A", "B", "AB", UNKNOWN],
}
MIN_DONOR_WEIGHT_KG = {"dog": 30.0, "cat": 4.0}
AGE_RANGE_YEARS = {"dog": (1, 6), "cat": (1, 7)}
DEFAULT_HOSPITALS = ["โรงพยาบาลสัตว์ คณะสัตวแพทยศาสตร์ มหาวิทยาลัยขอนแก่น"]


def case_blood_types(species: str) -> list[str]:
    return [b for b in BLOOD_TYPES[species] if b != UNKNOWN] + [UNSPECIFIED]


def age_years(birth: date, today: date | None = None) -> int:
    today = today or date.today()
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def fail(errors: list[str], code: int = status.HTTP_422_UNPROCESSABLE_ENTITY):
    """ตอบรายการข้อผิดพลาดหลายข้อพร้อมกัน เพื่อให้หน้าจอแจ้ง 'สิ่งที่ไม่ผ่านหรือลืมกรอก' ได้ครบ"""
    raise HTTPException(code, {"errors": errors})
