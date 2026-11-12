from pydantic import BaseModel


class StatsView(BaseModel):
    cases_searching: int   # เคสที่กำลังตามหา
    heroes_available: int  # ฮีโร่ที่พร้อมบริจาค
    cases_closed: int      # ปิดเคสสำเร็จ
