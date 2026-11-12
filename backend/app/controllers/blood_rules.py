from fastapi import HTTPException, status

BLOOD_TYPES = {
    "dog": {"DEA 1.1+", "DEA 1.1-", "ไม่ทราบ"},
    "cat": {"A", "B", "AB", "ไม่ทราบ"},
}
# เกณฑ์น้ำหนักขั้นต่ำของผู้บริจาค (ค่าตั้งต้นทั่วไป — ทีมควรยืนยันกับสัตวแพทย์)
MIN_DONOR_WEIGHT_KG = {"dog": 20.0, "cat": 4.0}


def check_blood_type(species: str, blood_type: str) -> None:
    if blood_type not in BLOOD_TYPES[species]:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "หมู่เลือดไม่ถูกต้องสำหรับชนิดสัตว์นี้")
