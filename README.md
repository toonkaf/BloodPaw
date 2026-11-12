# PetTech — ช่วยน้องหาเลือดได้เร็วขึ้น (MVC)

Mini Project: SOFTWARE DEVELOPMENT TOOLS AND ENVIRONMENTS (1/2569)
ระบบประกาศ "เคสด่วน" หาเลือดให้สัตว์ป่วย และลงทะเบียน "ฮีโร่" (สัตว์เลี้ยงผู้บริจาค) — หน้าจอทำตามแบบ Neumorphism ที่ออกแบบไว้

| ชั้น | Technology |
|---|---|
| View (UI) | React + Vite (hash routing), serve ด้วย Nginx |
| Controller + Routes | FastAPI (Python 3.12) |
| Model | SQLAlchemy + PostgreSQL 16 |
| Delivery | Git/GitHub, Docker Compose, Jenkins |

## โครงสร้าง

```
pettech/
├── backend/
│   ├── app/
│   │   ├── models/        # M  User, Hero, Case
│   │   ├── views/         # V  Pydantic schema
│   │   ├── controllers/   # C  Business Rule / AuthZ / Privacy
│   │   ├── routes/        #    URL -> Controller
│   │   └── core/          #    config, database, JWT
│   ├── tests/             #    pytest 18 เคส
│   └── Dockerfile         #    stage: test | runtime
├── frontend/src/
│   ├── views/             # V  Home, Cases, CaseForm, HeroForm, Auth, Profile
│   ├── components/        #    Navbar, CaseCard, Field
│   ├── api/client.js
│   └── styles.css         #    Neumorphism theme
├── docs/                  # architecture + traceability matrix
├── scripts/smoke-test.sh
├── docker-compose.yml
├── Jenkinsfile
└── .env.example
```

## เริ่มระบบ (ใน Course Container `tuchsanai/devtools:2569_1`)

```bash
cp .env.example .env
docker compose up -d --build --wait
./scripts/smoke-test.sh
# เปิด http://localhost:8080
docker compose down -v
```

## พัฒนาในเครื่อง

```bash
# Backend
cd backend && pip install -r requirements-dev.txt
DATABASE_URL=sqlite:// JWT_SECRET=test pytest -q
DATABASE_URL=sqlite:///./dev.db JWT_SECRET=dev uvicorn app.main:app --reload

# Frontend (proxy /api -> localhost:8000)
cd frontend && npm install && npm run dev
```

## API

| Method | Path | สิทธิ์ | หน้าที่ |
|---|---|---|---|
| GET | `/api/health` | ทุกคน | ตรวจสถานะ + DB |
| POST | `/api/auth/register`, `/api/auth/login` | ทุกคน | สมัคร / เข้าสู่ระบบ (JWT) |
| GET | `/api/stats` | ทุกคน | ตัวเลข Dashboard |
| GET | `/api/cases?status=&species=&province=&limit=` | ทุกคน (เบอร์ซ่อนถ้าไม่ล็อกอิน) | รายการเคส |
| POST | `/api/cases` | ล็อกอิน | ประกาศเคสด่วน |
| POST | `/api/cases/{id}/close` | เจ้าของเคส | ปิดเคส |
| GET | `/api/heroes` | ทุกคน (เบอร์ซ่อนถ้าไม่ล็อกอิน) | ฮีโร่ที่พร้อมบริจาค |
| POST | `/api/heroes` | ล็อกอิน | ลงทะเบียนฮีโร่ |
| PATCH | `/api/heroes/{id}` | เจ้าของ | เปิด/ปิดความพร้อมบริจาค |
| GET | `/api/me`, `/api/me/cases`, `/api/me/heroes` | ล็อกอิน | ข้อมูลโปรไฟล์ |

## ข้อสังเกตเทียบกับแบบหน้าจอ

- หน้า **เข้าสู่ระบบ** ในแบบมีช่อง "ชื่อ" ด้วย แต่ในโค้ดใช้ **อีเมล + รหัสผ่าน** เท่านั้น (ชื่อเก็บตอนสมัคร) ถ้าต้องการให้ล็อกอินด้วยชื่อ ต้องแก้ Model/Controller
- แบบหน้า **เคสด่วน** ยังไม่ระบุว่าการ์ดแสดงอะไร จึงออกแบบให้แสดงชื่อสัตว์ ชนิด หมู่เลือด โรงพยาบาล จังหวัด ความเร่งด่วน และเบอร์ติดต่อ (เฉพาะผู้ล็อกอิน)
- ขั้นตอน "ติดต่อยืนยัน" ทำเป็นการโทรหากันผ่านเบอร์ติดต่อ ยังไม่มีระบบแชท/แจ้งเตือนในแอป

## ที่ยังต้องทำ (TODO ของทีม)

- [ ] ตรวจเกณฑ์หมู่เลือด/น้ำหนักผู้บริจาคกับสัตวแพทย์ (`controllers/blood_rules.py`)
- [ ] แจ้งเตือนฮีโร่ที่หมู่เลือดตรงกับเคสใหม่ (ถ้าใช้ RabbitMQ/Celery หรือ LINE Notify ต้อง Demo ได้จริง)
- [ ] เปลี่ยน `create_all` เป็น Alembic migration
- [ ] Prometheus/Grafana หรือ Log รวม ถ้าอ้างว่ามี
- [ ] ใส่ผลจริงใน `docs/traceability-matrix.md`
- [ ] สรุปการใช้ AI Coding Tools
