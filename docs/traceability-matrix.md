# Traceability Matrix (ตัวอย่างเริ่มต้น — แก้ตาม Proposal ของทีม)

| ID | Requirement | Acceptance Criteria | ส่วนที่นำไปใช้ | วิธีตรวจ | ผลจริง/สถานะ |
|---|---|---|---|---|---|
| R1 | สมัคร/เข้าสู่ระบบ | รหัสผ่านผิดแจ้งข้อความเดียวกันทุกกรณี; รหัสผ่าน ≥ 8 ตัว | `auth_controller`, `AuthViews` | `tests/test_auth.py`, UI | _ใส่ผลจริง_ |
| R2 | ประกาศเคสด่วน | บันทึกเคสสถานะ "กำลังตามหา"; หมู่เลือดต้องตรงชนิดสัตว์; เบอร์ถูกรูปแบบ | `case_controller`, `CaseFormView` | `tests/test_cases.py` | _ใส่ผลจริง_ |
| R3 | ลงทะเบียนฮีโร่ | ผ่านเกณฑ์น้ำหนัก; ฮีโร่ที่ "พักก่อน" ไม่แสดงในรายการ | `hero_controller`, `HeroFormView` | `tests/test_heroes_stats.py` | _ใส่ผลจริง_ |
| R4 | Dashboard หน้าหลัก | ตัวเลข 3 ช่องตรงกับข้อมูลจริง | `stats_controller`, `HomeView` | `test_stats_match_data`, smoke test | _ใส่ผลจริง_ |
| R5 | ปิดเคสสำเร็จ | เฉพาะเจ้าของปิดได้; ปิดซ้ำไม่ได้; ตัวเลข "ปิดเคสสำเร็จ" เพิ่ม | `case_controller.close` | `test_only_owner_can_close`, `test_close_twice_conflicts` | _ใส่ผลจริง_ |
| R6 | ความเป็นส่วนตัว | เบอร์ติดต่อเห็นเฉพาะผู้ล็อกอิน | `_view()` ใน controllers | `test_contact_hidden_from_anonymous`, smoke test | _ใส่ผลจริง_ |
| R7 | ส่งมอบอัตโนมัติ | Test ไม่ผ่าน → ไม่ Deploy | `Jenkinsfile` | รัน Pipeline ที่ตั้งใจให้ Fail 1 ครั้ง | _ใส่ผลจริง_ |
| R8 | รันซ้ำได้ใน Course Container | `docker compose up` แล้ว smoke test ผ่าน | `docker-compose.yml`, `scripts/smoke-test.sh` | รันใน `tuchsanai/devtools:2569_1` | _ใส่ผลจริง_ |
