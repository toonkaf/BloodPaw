import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET", "test-secret")

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def client():
    return TestClient(app)


def make_user(client, email="a@example.com"):
    client.post("/api/auth/register", json={"email": email, "password": "password123", "full_name": "A"})
    token = client.post("/api/auth/login", json={"email": email, "password": "password123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


CASE = {"pet_name": "ข้าวโพด", "species": "dog", "blood_type": "DEA 1.1-", "hospital": "รพ.สัตว์ A",
        "province": "กรุงเทพมหานคร", "urgency": "critical", "contact_phone": "0812345678"}
HERO = {"name": "บราวนี่", "species": "dog", "blood_type": "DEA 1.1-", "weight_kg": 28,
        "province": "กรุงเทพมหานคร", "contact_phone": "0898765432"}
