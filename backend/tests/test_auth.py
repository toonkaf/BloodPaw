from tests.conftest import make_user


def test_register_and_login(client):
    h = make_user(client)
    assert client.get("/api/me", headers=h).json()["email"] == "a@example.com"


def test_duplicate_email_rejected(client):
    make_user(client)
    r = client.post("/api/auth/register", json={"email": "a@example.com", "password": "password123", "full_name": "A"})
    assert r.status_code == 409


def test_weak_password_lists_every_problem(client):
    r = client.post("/api/auth/register", json={"email": "x@example.com", "password": "abc", "full_name": "X"})
    errors = r.json()["detail"]["errors"]
    assert r.status_code == 422 and len(errors) == 2


def test_wrong_password_name_or_email_all_get_same_message(client):
    make_user(client, name="สมชาย")
    attempts = [
        {"email": "a@example.com", "password": "wrongpass1", "full_name": "สมชาย"},
        {"email": "a@example.com", "password": "password123", "full_name": "คนอื่น"},
        {"email": "none@example.com", "password": "password123", "full_name": "สมชาย"},
    ]
    for body in attempts:
        r = client.post("/api/auth/login", json=body)
        assert r.status_code == 401 and r.json()["detail"] == "อีเมลหรือรหัสผ่านไม่ถูกต้อง"


def test_protected_route_requires_token(client):
    assert client.get("/api/me/cases").status_code == 401
    assert client.post("/api/heroes", json={}).status_code == 401
