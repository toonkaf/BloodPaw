from tests.conftest import add_case, case_payload, make_user


def test_create_case_requires_login(client):
    assert client.post("/api/cases", json=case_payload()).status_code == 401


def test_public_case_never_exposes_phone(client):
    h = make_user(client)
    add_case(client, h)
    row = client.get("/api/cases").json()[0]
    assert "contact_phone" not in row and "owner_id" not in row and row["status"] == "searching"


def test_blood_type_must_match_species(client):
    h = make_user(client)
    r = client.post("/api/cases", json=case_payload(blood_type="AB"), headers=h)
    assert r.status_code == 422
    assert client.post("/api/cases", json=case_payload(blood_type="ไม่ระบุ"), headers=h).status_code == 201


def test_filters_by_hospital_species_blood_urgency(client):
    h = make_user(client)
    add_case(client, h, hospital="รพ.สัตว์ A", urgency="urgent")
    add_case(client, h, hospital="รพ.สัตว์ B", urgency="advance", species="cat", blood_type="A")
    assert len(client.get("/api/cases?hospital=รพ.สัตว์ B").json()) == 1
    assert len(client.get("/api/cases?species=cat").json()) == 1
    assert len(client.get("/api/cases?blood_type=DEA 1.2").json()) == 1
    assert len(client.get("/api/cases?urgency=urgent").json()) == 1
    assert len(client.get("/api/cases?urgency=critical").json()) == 0


def test_sorted_by_urgency_then_newest(client):
    h = make_user(client)
    for name, urg in [("a", "advance"), ("b", "critical"), ("c", "urgent"), ("d", "critical")]:
        add_case(client, h, pet_name=name, urgency=urg)
    assert [c["pet_name"] for c in client.get("/api/cases").json()] == ["d", "b", "c", "a"]
    assert [c["pet_name"] for c in client.get("/api/cases?sort=latest&limit=2").json()] == ["d", "c"]


def test_invalid_urgency_rejected(client):
    h = make_user(client)
    assert client.post("/api/cases", json=case_payload(urgency="normal"), headers=h).status_code == 422


def test_meta_lists_hospitals_from_data(client):
    h = make_user(client)
    add_case(client, h, hospital="รพ.สัตว์ ทดสอบ")
    meta = client.get("/api/meta").json()
    assert "รพ.สัตว์ ทดสอบ" in meta["hospitals"] and meta["min_donor_weight"]["dog"] == 30
