import os
import tempfile
from datetime import date, timedelta

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ["UPLOAD_DIR"] = tempfile.mkdtemp()

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def client():
    return TestClient(app)


def make_user(client, email="a@example.com", name="A"):
    client.post("/api/auth/register", json={"email": email, "password": "password123", "full_name": name})
    r = client.post("/api/auth/login", json={"email": email, "password": "password123", "full_name": name})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def hero_payload(**kw):
    base = {"name": "บราวนี่", "species": "dog", "breed": "โกลเด้น", "weight_kg": 32, "blood_type": "DEA 1.2",
            "birth_date": (date.today() - timedelta(days=365 * 3 + 30)).isoformat(),
            "vaccinated_ok": True, "no_chronic_disease": True, "criteria_confirmed": True,
            "hospitals": ["รพ.สัตว์ A"], "province": "ขอนแก่น", "contact_phone": "0898765432"}
    return {**base, **kw}


def case_payload(**kw):
    base = {"species": "dog", "pet_name": "น้องหลงทาง", "breed": "บางแก้ว", "symptom": "เสียเลือดมาก",
            "cause": "ถูกรถชนขาหัก", "blood_type": "DEA 1.2", "hospital": "รพ.สัตว์ A",
            "contact_phone": "0812345678", "urgency": "critical"}
    return {**base, **kw}


def add_hero(client, headers, **kw):
    r = client.post("/api/heroes", json=hero_payload(**kw), headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def add_case(client, headers, **kw):
    r = client.post("/api/cases", json=case_payload(**kw), headers=headers)
    assert r.status_code == 201, r.text
    return r.json()
