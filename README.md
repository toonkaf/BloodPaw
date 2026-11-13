# PetTech — ช่วยน้องหาเลือดได้เร็วขึ้น (MVC)

Mini Project: SOFTWARE DEVELOPMENT TOOLS AND ENVIRONMENTS (1/2569)
ระบบประกาศ "เคสด่วน" หาเลือดให้สัตว์ป่วย และลงทะเบียน "ฮีโร่" (สัตว์เลี้ยงผู้บริจาค) โดย **ระบบจับคู่ให้อัตโนมัติ** แล้วให้เจ้าของทั้งสองฝ่ายคุยและยืนยันผ่านระบบ — ทำตามแบบหน้าจอ 10 หน้าและเอกสาร User Flow

| ชั้น | Technology |
|---|---|
| View (UI) | React + Vite (hash routing), serve ด้วย Nginx |
| Controller + Routes | FastAPI (Python 3.12) |
| Model | SQLAlchemy + PostgreSQL 16 |
| ไฟล์รูป | Docker volume `uploads` |
| Delivery | Git/GitHub, Docker Compose, Jenkins |

## โครงสร้าง

```
pettech/
├── backend/
│   ├── app/
│   │   ├── models/        # M  User, Hero, Case, Match, Message
│   │   ├── views/         # V  Pydantic schema (กำหนดว่าข้อมูลใดส่งออกได้)
│   │   ├── controllers/   # C  Business Rule, matching.py (จับคู่), rules.py (เกณฑ์)
│   │   ├── routes/        #    URL -> Controller
│   │   └── core/          #    config, database, JWT
│   ├── tests/             #    pytest 41 เคส
│   └── Dockerfile         #    stage: test | runtime
├── frontend/src/
│   ├── views/             # V  Home, Cases, Auth, CaseForm, HeroForm(สร้าง/แก้ไข), Profile, Match(แชท)
│   ├── components/        #    Navbar, Cards, PhotoUpload, HospitalPicker, Alerts
│   ├── lib/               #    format.js, criteria.js (เกณฑ์การบริจาค)
│   └── styles.css         #    Neumorphism theme
├── docs/                  # architecture + traceability matrix
├── scripts/smoke-test.sh
├── docker-compose.yml
├── Jenkinsfile
└── .env.example
```

## เริ่มระบบ (ใน Course Container `tuchsanai/devtools:2569_1`)

```bash
cp .env.example .env            # แก้ค่า secret และ WEB_PORT ให้ตรงกับพอร์ตที่เปิดจากกล่อง
docker compose up -d --build --wait
bash scripts/smoke-test.sh
# เปิด http://localhost:<WEB_PORT>
docker compose down -v          # เก็บกวาด
```

> **อัปเกรดจากเวอร์ชันก่อนหน้า:** โครงสร้างตารางเปลี่ยน (`create_all` ไม่แก้ตารางเดิม) ต้องรัน `docker compose down -v` ก่อน `up` ใหม่ ข้อมูลทดสอบเดิมจะหาย

## พัฒนาในเครื่อง

```bash
# Backend
cd backend && pip install -r requirements-dev.txt
DATABASE_URL=sqlite:// JWT_SECRET=test pytest -q
DATABASE_URL=sqlite:///./dev.db JWT_SECRET=dev UPLOAD_DIR=./uploads uvicorn app.main:app --reload

# Frontend (proxy /api -> localhost:8000)
cd frontend && npm install && npm run dev
```

## วิธีใช้งานตาม User Flow

1. **สมัครสมาชิก / เข้าสู่ระบบ** (ชื่อ + อีเมล + รหัสผ่าน; รหัสผ่านอย่างน้อย 8 ตัว มีทั้งตัวอักษรและตัวเลข)
2. **ลงทะเบียนฮีโร่** — กรอกข้อมูลสัตว์ สุขภาพ ติ๊กยืนยันเกณฑ์ เลือกโรงพยาบาลที่สะดวก (หลายแห่งได้) ระบบตรวจเกณฑ์และแจ้งทุกข้อที่ไม่ผ่าน
3. **ประกาศเคสด่วน** — กรอกข้อมูลสัตว์ป่วย เงื่อนไข โรงพยาบาล และเลือกระดับ ล่วงหน้า/ด่วน/ด่วนมาก
4. ระบบ **จับคู่อัตโนมัติ** → เจ้าของฮีโร่เห็นที่ **โปรไฟล์ > คำขอที่ได้รับ**, เจ้าของเคสเห็นสถานะ "พบฮีโร่"
5. กด **ติดต่อสอบถาม** เพื่อแชท / กด **tel.** เพื่อส่งเบอร์โทรให้อีกฝ่าย
6. กด **ยืนยัน/สำเร็จ** (เคสปิด) หรือ **ปฏิเสธ** (ระบบหาคู่ใหม่ให้เคส)
7. ฮีโร่ไม่พร้อม → สลับ **พัก** ที่โปรไฟล์ (คำขอที่ค้างจะถูกส่งต่อให้ฮีโร่ตัวอื่น)

## API

| Method | Path | สิทธิ์ | หน้าที่ |
|---|---|---|---|
| GET | `/api/health`, `/api/stats`, `/api/meta` | ทุกคน | สถานะ / Dashboard / รายการโรงพยาบาลและกติกา |
| POST | `/api/auth/register`, `/api/auth/login` | ทุกคน | สมัคร / เข้าสู่ระบบ (JWT) |
| GET | `/api/cases?hospital=&species=&blood_type=&urgency=&sort=&limit=` | ทุกคน | เคสที่ยังไม่สำเร็จ (ไม่มีเบอร์โทร) |
| GET | `/api/uploads/{name}` | ทุกคน | ไฟล์รูป |
| POST | `/api/uploads` | ล็อกอิน | อัปโหลดรูป (JPG/PNG/WEBP ≤ 2 MB) |
| POST | `/api/cases` | ล็อกอิน | ประกาศเคส (แล้วจับคู่ทันที) |
| POST/PUT | `/api/heroes`, `/api/heroes/{id}` | ล็อกอิน / เจ้าของ | ลงทะเบียน / แก้ไขฮีโร่ |
| PATCH | `/api/heroes/{id}/status` | เจ้าของ | พัก / พร้อม |
| GET | `/api/me`, `/api/me/heroes`, `/api/me/cases`, `/api/me/requests` | ล็อกอิน | โปรไฟล์ |
| GET | `/api/matches/{id}` | 2 ฝ่ายของคู่นั้น | หน้าติดต่อ (การ์ด + แชท) |
| POST | `/api/matches/{id}/messages`, `/share-phone`, `/decline`, `/confirm` | 2 ฝ่ายของคู่นั้น | ส่งข้อความ / ส่งเบอร์ / ปฏิเสธ / ยืนยัน |

## ข้อสังเกตเทียบกับแบบ/ User Flow

- **เบอร์โทรไม่เปิดเผยเลย** แม้กับผู้ที่ล็อกอิน จะส่งถึงอีกฝ่ายเฉพาะเมื่อกดปุ่ม tel ในแชทของคู่นั้น (ตามคำอธิบาย "ไม่เปิดเผยสู่สาธารณะ")
- **Dashboard "เคสที่กำลังตามหา"** นับเฉพาะเคสที่ยังไม่พบฮีโร่ (สถานะ searching); เคสที่ "พบฮีโร่" แล้วไม่นับในช่องใด จนกว่าจะสำเร็จ
- **ฮีโร่ 1 ตัวถือคำขอได้ทีละ 1 เคส** และถ้าไม่ทราบหมู่เลือด ระบบถือว่าสัตวแพทย์จะตรวจก่อนบริจาค จึงจับกับเคสใดก็ได้ที่เงื่อนไขอื่นผ่าน
- รายละเอียดข้อจำกัดอื่น ๆ ดู `docs/architecture.md` หัวข้อ "ข้อจำกัดที่ทราบ"

## ที่ยังต้องทำ (TODO ของทีม)

- [ ] ตรวจเกณฑ์หมู่เลือด/อายุ/น้ำหนักผู้บริจาคกับสัตวแพทย์ (`controllers/rules.py`, `frontend/src/lib/criteria.js`)
- [ ] ตารางโรงพยาบาลกลาง (ตอนนี้เทียบชื่อแบบตรงตัว)
- [ ] แจ้งเตือนเมื่อได้รับคำขอ (ถ้าทำ LINE/อีเมล/RabbitMQ ต้อง Demo ได้จริง) และเปลี่ยนแชทเป็น WebSocket ถ้าต้องการ
- [ ] เปลี่ยน `create_all` เป็น Alembic migration
- [ ] Prometheus/Grafana หรือ Log รวม ถ้าอ้างว่ามี
- [ ] ใส่ผลจริงใน `docs/traceability-matrix.md`
- [ ] สรุปการใช้ AI Coding Tools
