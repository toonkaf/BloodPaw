# Traceability Matrix (อ้างอิงเอกสาร User Flow 10 หน้า — เติม "ผลจริง" ตอนทดสอบ)

| ID | หน้า/Requirement (จาก User Flow) | Acceptance Criteria | ส่วนที่นำไปใช้ | วิธีตรวจ | ผลจริง |
|---|---|---|---|---|---|
| R1 | เข้าสู่ระบบ | ผิดช่องใดก็แจ้ง "อีเมลหรือรหัสผ่านไม่ถูกต้อง" โดยไม่บอกว่าผิดช่องไหน; ยังไม่มีบัญชีกดไปสมัครได้ | `auth_controller.login`, `AuthViews` | `test_wrong_password_name_or_email_all_get_same_message`, smoke test | _ใส่_ |
| R2 | สมัครสมาชิก | ตรวจมาตรฐานรหัสผ่าน + บัญชีไม่ซ้ำ + สมัครเสร็จถือว่าเข้าสู่ระบบแล้ว | `auth_controller.register`, `RegisterView` | `test_weak_password_lists_every_problem`, `test_duplicate_email_rejected`, E2E | _ใส่_ |
| R3 | หน้าหลัก | Dashboard 3 ค่าตรงข้อมูลจริง; เคสล่าสุด; ปุ่มลงทะเบียน/ประกาศพาไปหน้าที่ถูกต้อง (ต้องล็อกอิน) | `stats_controller`, `HomeView`, `App` (route guard) | `test_stats_counts`, `test_confirm_closes_case_updates_stats…` | _ใส่_ |
| R4 | เคสด่วน | แสดงเฉพาะเคสที่ยังไม่สำเร็จ; กรองตาม โรงพยาบาล/ชนิด/กรุ๊ปเลือด/ระดับ | `case_controller.list_open`, `CasesView` | `test_filters_by_hospital_species_blood_urgency`, `test_sorted_by_urgency_then_newest` | _ใส่_ |
| R5 | ลงทะเบียนฮีโร่ | เกณฑ์ตามชนิดสัตว์; ตรวจเกณฑ์แล้วแจ้ง "สิ่งที่ไม่ผ่านหรือลืมกรอก" ครบทุกข้อ; สำเร็จไปหน้าโปรไฟล์; มีอัปโหลดรูป | `hero_controller._check`, `HeroFormView`, `upload_controller` | `test_all_failed_criteria_reported_together`, `test_cat_has_its_own_criteria`, `test_uploads.py`, E2E | _ใส่_ |
| R6 | ประกาศเคสด่วน | กรอกครบแล้วบันทึกทุกข้อมูล ไปหน้าโปรไฟล์; เลือกระดับ ล่วงหน้า/ด่วน/ด่วนมาก | `case_controller.create`, `CaseFormView` | `test_blood_type_must_match_species`, `test_invalid_urgency_rejected` | _ใส่_ |
| R7 | โปรไฟล์: ฮีโร่ + พัก/พร้อม | เปลี่ยนเป็น "พัก" → ยกเลิกคำขอที่จับไว้ ส่งเคสไปจับใหม่ และไม่ถูกจับอีกจนกว่าจะ "พร้อม" | `hero_controller.set_status`, `matching.cancel_pending` | `test_resting_hero_cancels_request_and_is_not_matched_until_ready`, `test_resting_hero_hands_case_to_another_hero` | _ใส่_ |
| R8 | โปรไฟล์: คำขอที่ได้รับ | ระบบจับคู่เคสให้ฮีโร่; ปฏิเสธ → ลบแล้วจับใหม่; ยืนยัน → เคสสำเร็จ | `matching.run_matching`, `match_controller` | `test_case_then_hero_auto_matches`, `test_decline_rematches_…`, `test_confirm_closes_case…` | _ใส่_ |
| R9 | โปรไฟล์: เคสที่ฉันประกาศ | จับคู่ได้แล้วกดติดต่อ/ยืนยันได้ | `OwnCaseView.match_id`, `ProfileView` | `test_hero_then_case_auto_matches`, E2E | _ใส่_ |
| R10 | หน้าติดต่อเคสด่วน/ฮีโร่ | แชทผ่านระบบ; ปุ่ม tel ส่งเบอร์ที่กรอกไว้ตอนลงทะเบียน/ประกาศให้อีกฝ่ายทันที; ปฏิเสธ/ยืนยันได้ | `match_controller`, `MatchView` | `test_chat_and_phone_share_go_to_the_right_person`, `test_outsider_cannot_see_or_use_match` | _ใส่_ |
| R11 | แก้ไขข้อมูลฮีโร่ | ดึงข้อมูลเดิมมาใส่; ตรวจเกณฑ์เหมือนลงทะเบียน; สำเร็จกลับโปรไฟล์ | `hero_controller.update`, `HeroFormView(heroId)` | `test_edit_hero_prefill_and_save`, `test_editing_hero_out_of_eligibility_cancels_request` | _ใส่_ |
| R12 | Navbar | ลงทะเบียนฮีโร่/ประกาศเคส กดได้เมื่อล็อกอิน; ปุ่มเข้าสู่ระบบเปลี่ยนเป็นโปรไฟล์ | `Navbar`, `App` | E2E / ตรวจด้วยตา | _ใส่_ |
| R13 | ความเป็นส่วนตัว (เพิ่มจากทีม) | เบอร์โทรไม่เปิดเผยสู่สาธารณะ | Pydantic view ไม่มี field เบอร์; `share_phone` | `test_public_case_never_exposes_phone`, smoke test | _ใส่_ |
| R14 | ส่งมอบอัตโนมัติ | Test ไม่ผ่าน → ไม่ Deploy | `Jenkinsfile` | รัน Pipeline ที่ตั้งใจให้ Fail 1 ครั้ง | _ใส่_ |
| R15 | รันซ้ำได้ใน Course Container | `docker compose up` แล้ว smoke test ผ่าน | `docker-compose.yml`, `scripts/smoke-test.sh` | รันใน `tuchsanai/devtools:2569_1` | _ใส่_ |
