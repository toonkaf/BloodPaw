from pydantic import BaseModel


class StatsView(BaseModel):
    cases_searching: int   # เคสที่กำลังตามหา (ยังไม่พบฮีโร่)
    heroes_available: int  # ฮีโร่ที่พร้อมบริจาค
    cases_success: int     # ปิดเคสสำเร็จ


class MetaView(BaseModel):
    hospitals: list[str]
    hero_blood_types: dict[str, list[str]]
    case_blood_types: dict[str, list[str]]
    min_donor_weight: dict[str, float]
    age_range: dict[str, list[int]]
