from typing import Literal

Species = Literal["dog", "cat"]
Urgency = Literal["advance", "urgent", "critical"]   # ล่วงหน้า | ด่วน | ด่วนมาก
PHONE = r"^0\d{8,9}$"
PHOTO = r"^/api/uploads/[0-9a-f]{32}\.(jpg|png|webp)$"
