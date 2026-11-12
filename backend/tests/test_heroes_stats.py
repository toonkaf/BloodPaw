from tests.conftest import CASE, HERO, make_user


def test_register_hero_and_list(client):
    h = make_user(client)
    assert client.post("/api/heroes", json=HERO, headers=h).status_code == 201
    heroes = client.get("/api/heroes").json()
    assert len(heroes) == 1 and heroes[0]["contact_phone"] is None


def test_underweight_dog_rejected(client):
    h = make_user(client)
    r = client.post("/api/heroes", json={**HERO, "weight_kg": 8}, headers=h)
    assert r.status_code == 422


def test_unavailable_hero_not_listed(client):
    h = make_user(client)
    hid = client.post("/api/heroes", json=HERO, headers=h).json()["id"]
    client.patch(f"/api/heroes/{hid}", json={"available": False}, headers=h)
    assert client.get("/api/heroes").json() == []


def test_cannot_toggle_other_users_hero(client):
    h1, h2 = make_user(client, "a@example.com"), make_user(client, "b@example.com")
    hid = client.post("/api/heroes", json=HERO, headers=h1).json()["id"]
    assert client.patch(f"/api/heroes/{hid}", json={"available": False}, headers=h2).status_code == 404


def test_stats_match_data(client):
    h = make_user(client)
    assert client.get("/api/stats").json() == {"cases_searching": 0, "heroes_available": 0, "cases_closed": 0}
    client.post("/api/heroes", json=HERO, headers=h)
    c1 = client.post("/api/cases", json=CASE, headers=h).json()["id"]
    client.post("/api/cases", json=CASE, headers=h)
    client.post(f"/api/cases/{c1}/close", headers=h)
    assert client.get("/api/stats").json() == {"cases_searching": 1, "heroes_available": 1, "cases_closed": 1}


def test_my_cases_only_own(client):
    h1, h2 = make_user(client, "a@example.com"), make_user(client, "b@example.com")
    client.post("/api/cases", json=CASE, headers=h1)
    assert len(client.get("/api/me/cases", headers=h1).json()) == 1
    assert client.get("/api/me/cases", headers=h2).json() == []
