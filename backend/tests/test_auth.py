from tests.conftest import make_user


def test_register_and_login(client):
    headers = make_user(client)
    assert client.get("/api/me", headers=headers).json()["email"] == "a@example.com"


def test_duplicate_email_rejected(client):
    make_user(client)
    r = client.post("/api/auth/register", json={"email": "a@example.com", "password": "password123", "full_name": "A"})
    assert r.status_code == 409


def test_wrong_password_generic_message(client):
    make_user(client)
    r = client.post("/api/auth/login", json={"email": "a@example.com", "password": "wrongpass1"})
    assert r.status_code == 401
    assert r.json()["detail"] == "อีเมลหรือรหัสผ่านไม่ถูกต้อง"


def test_protected_route_requires_token(client):
    assert client.get("/api/me/cases").status_code == 401
