from datetime import date, timedelta

from tests.conftest import add_hero, hero_payload, make_user


def _errors(r):
    assert r.status_code == 422, r.text
    return r.json()["detail"]["errors"]


def test_register_hero_and_own_view_has_phone(client):
    h = make_user(client)
    add_hero(client, h)
    mine = client.get("/api/me/heroes", headers=h).json()
    assert len(mine) == 1 and mine[0]["contact_phone"] == "0898765432" and mine[0]["status"] == "ready"


def test_all_failed_criteria_reported_together(client):
    h = make_user(client)
    bad = hero_payload(weight_kg=10, vaccinated_ok=False, no_chronic_disease=False, criteria_confirmed=False,
                       birth_date=(date.today() - timedelta(days=100)).isoformat(), blood_type="AB")
    errs = _errors(client.post("/api/heroes", json=bad, headers=h))
    assert len(errs) == 6  # หมู่เลือด, อายุ, น้ำหนัก, วัคซีน, โรคเรื้อรัง, ยืนยันเกณฑ์
    assert any("อายุ" in e for e in errs) and any("30" in e for e in errs)


def test_cat_has_its_own_criteria(client):
    h = make_user(client)
    cat = hero_payload(species="cat", blood_type="A", weight_kg=4.5, birth_date=(date.today() - timedelta(days=365 * 8 + 100)).isoformat())
    assert any("1-7" in e for e in _errors(client.post("/api/heroes", json=cat, headers=h)))  # แมวอายุ 8 ปีกว่า เกินเกณฑ์ 1-7 ปี
    cat["birth_date"] = (date.today() - timedelta(days=365 * 2 + 30)).isoformat()
    assert client.post("/api/heroes", json=cat, headers=h).status_code == 201


def test_missing_or_bad_fields_named_in_thai(client):
    h = make_user(client)
    body = hero_payload(contact_phone="123")
    del body["breed"]
    errs = _errors(client.post("/api/heroes", json=body, headers=h))
    assert any("สายพันธุ์" in e for e in errs) and any("เบอร์โทร" in e for e in errs)


def test_edit_hero_prefill_and_save(client):
    h = make_user(client)
    hero = add_hero(client, h)
    r = client.put(f"/api/heroes/{hero['id']}", json=hero_payload(name="ใหม่", weight_kg=35, hospitals=["รพ.สัตว์ A", "รพ.สัตว์ B"]), headers=h)
    assert r.status_code == 200 and r.json()["name"] == "ใหม่" and len(r.json()["hospitals"]) == 2
    assert client.put(f"/api/heroes/{hero['id']}", json=hero_payload(weight_kg=5), headers=h).status_code == 422


def test_cannot_edit_or_change_status_of_others_hero(client):
    h1, h2 = make_user(client, "a@example.com"), make_user(client, "b@example.com")
    hero = add_hero(client, h1)
    assert client.put(f"/api/heroes/{hero['id']}", json=hero_payload(), headers=h2).status_code == 404
    assert client.patch(f"/api/heroes/{hero['id']}/status", json={"status": "resting"}, headers=h2).status_code == 404


def test_hospital_list_deduplicated(client):
    h = make_user(client)
    hero = add_hero(client, h, hospitals=["รพ.สัตว์ A", "  รพ.สัตว์   A ", "รพ.สัตว์ B"])
    assert hero["hospitals"] == ["รพ.สัตว์ A", "รพ.สัตว์ B"]
