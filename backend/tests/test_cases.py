from tests.conftest import CASE, make_user


def test_create_case_requires_login(client):
    assert client.post("/api/cases", json=CASE).status_code == 401


def test_create_and_list_case(client):
    h = make_user(client)
    r = client.post("/api/cases", json=CASE, headers=h)
    assert r.status_code == 201 and r.json()["status"] == "searching"
    assert len(client.get("/api/cases?status=searching").json()) == 1


def test_invalid_blood_type_for_species_rejected(client):
    h = make_user(client)
    r = client.post("/api/cases", json={**CASE, "blood_type": "AB"}, headers=h)  # AB เป็นหมู่เลือดแมว
    assert r.status_code == 422


def test_invalid_phone_rejected(client):
    h = make_user(client)
    assert client.post("/api/cases", json={**CASE, "contact_phone": "123"}, headers=h).status_code == 422


def test_contact_hidden_from_anonymous(client):
    h = make_user(client)
    client.post("/api/cases", json=CASE, headers=h)
    assert client.get("/api/cases").json()[0]["contact_phone"] is None
    assert client.get("/api/cases", headers=h).json()[0]["contact_phone"] == "0812345678"


def test_critical_cases_listed_first(client):
    h = make_user(client)
    client.post("/api/cases", json={**CASE, "pet_name": "normal", "urgency": "normal"}, headers=h)
    client.post("/api/cases", json={**CASE, "pet_name": "critical", "urgency": "critical"}, headers=h)
    assert client.get("/api/cases?status=searching").json()[0]["pet_name"] == "critical"


def test_only_owner_can_close(client):
    h1, h2 = make_user(client, "a@example.com"), make_user(client, "b@example.com")
    cid = client.post("/api/cases", json=CASE, headers=h1).json()["id"]
    assert client.post(f"/api/cases/{cid}/close", headers=h2).status_code == 403
    assert client.post(f"/api/cases/{cid}/close", headers=h1).json()["status"] == "closed"


def test_close_twice_conflicts(client):
    h = make_user(client)
    cid = client.post("/api/cases", json=CASE, headers=h).json()["id"]
    client.post(f"/api/cases/{cid}/close", headers=h)
    assert client.post(f"/api/cases/{cid}/close", headers=h).status_code == 409
