from tests.conftest import add_case, add_hero, hero_payload, make_user


def _users(client):
    return make_user(client, "owner@example.com", "Owner"), make_user(client, "donor@example.com", "Donor")


def _request_ids(client, headers):
    return [r["match_id"] for r in client.get("/api/me/requests", headers=headers).json()]


def test_case_then_hero_auto_matches(client):
    owner, donor = _users(client)
    case = add_case(client, owner)
    assert case["status"] == "searching" and case["match_id"] is None
    add_hero(client, donor)                                   # ฮีโร่มาทีหลัง ระบบจับให้ทันที
    mine = client.get("/api/me/cases", headers=owner).json()[0]
    assert mine["status"] == "found" and mine["match_id"] is not None
    assert len(_request_ids(client, donor)) == 1


def test_hero_then_case_auto_matches(client):
    owner, donor = _users(client)
    add_hero(client, donor)
    case = add_case(client, owner)
    assert case["status"] == "found" and case["match_id"] is not None


def test_no_match_when_not_eligible(client):
    owner, donor = _users(client)
    add_hero(client, donor, hospitals=["รพ.สัตว์ อื่น"])                              # ไม่สะดวกที่โรงพยาบาลนี้
    add_hero(client, donor, blood_type="DEA 1.1+")                                    # หมู่เลือดไม่ตรง
    add_hero(client, donor, species="cat", blood_type="A", weight_kg=5)               # คนละชนิด
    add_hero(client, owner)                                                           # สัตว์ของเจ้าของเคสเอง
    assert add_case(client, owner)["status"] == "searching"


def test_unknown_blood_type_hero_can_match_but_exact_match_preferred(client):
    owner, donor = _users(client)
    other = make_user(client, "other@example.com", "Other")
    add_hero(client, donor, blood_type="ไม่ทราบ")
    exact = add_hero(client, other, blood_type="DEA 1.2")
    case = add_case(client, owner)
    assert case["status"] == "found"
    assert len(_request_ids(client, other)) == 1 and _request_ids(client, donor) == []
    assert exact["status"] == "ready"


def test_critical_case_gets_the_only_hero_first(client):
    owner, donor = _users(client)
    add_case(client, owner, pet_name="ล่วงหน้า", urgency="advance")
    add_case(client, owner, pet_name="ด่วนมาก", urgency="critical")
    add_hero(client, donor)
    by_name = {c["pet_name"]: c["status"] for c in client.get("/api/me/cases", headers=owner).json()}
    assert by_name == {"ล่วงหน้า": "searching", "ด่วนมาก": "found"}


def test_hero_holds_one_request_at_a_time(client):
    owner, donor = _users(client)
    add_hero(client, donor)
    add_case(client, owner, pet_name="1")
    add_case(client, owner, pet_name="2")
    assert len(_request_ids(client, donor)) == 1


def test_decline_rematches_to_another_hero_and_never_back_to_same(client):
    owner, donor = _users(client)
    other = make_user(client, "other@example.com", "Other")
    add_hero(client, donor)
    add_case(client, owner)
    first = _request_ids(client, donor)[0]
    add_hero(client, other)                                   # ฮีโร่ตัวที่ 2 รอสำรอง
    assert client.post(f"/api/matches/{first}/decline", headers=donor).status_code == 200
    assert _request_ids(client, donor) == [] and len(_request_ids(client, other)) == 1
    second = _request_ids(client, other)[0]
    client.post(f"/api/matches/{second}/decline", headers=other)
    assert client.get("/api/me/cases", headers=owner).json()[0]["status"] == "searching"  # ไม่วนกลับไปหาคนที่ปฏิเสธ


def test_case_owner_can_also_decline_hero(client):
    owner, donor = _users(client)
    add_hero(client, donor)
    case = add_case(client, owner)
    assert client.post(f"/api/matches/{case['match_id']}/decline", headers=owner).status_code == 200
    assert client.get("/api/me/cases", headers=owner).json()[0]["status"] == "searching"


def test_resting_hero_cancels_request_and_is_not_matched_until_ready(client):
    owner, donor = _users(client)
    hero = add_hero(client, donor)
    add_case(client, owner)
    client.patch(f"/api/heroes/{hero['id']}/status", json={"status": "resting"}, headers=donor)
    assert _request_ids(client, donor) == []
    assert client.get("/api/me/cases", headers=owner).json()[0]["status"] == "searching"
    client.patch(f"/api/heroes/{hero['id']}/status", json={"status": "ready"}, headers=donor)
    assert len(_request_ids(client, donor)) == 1               # กลับมาพร้อม -> ถูกจับได้อีก


def test_resting_hero_hands_case_to_another_hero(client):
    owner, donor = _users(client)
    other = make_user(client, "other@example.com", "Other")
    hero = add_hero(client, donor)
    add_case(client, owner)
    add_hero(client, other)
    client.patch(f"/api/heroes/{hero['id']}/status", json={"status": "resting"}, headers=donor)
    assert len(_request_ids(client, other)) == 1


def test_editing_hero_out_of_eligibility_cancels_request(client):
    owner, donor = _users(client)
    hero = add_hero(client, donor)
    add_case(client, owner)
    client.put(f"/api/heroes/{hero['id']}", json=hero_payload(hospitals=["รพ.สัตว์ อื่น"]), headers=donor)
    assert _request_ids(client, donor) == []
    assert client.get("/api/me/cases", headers=owner).json()[0]["status"] == "searching"


def test_confirm_closes_case_updates_stats_and_locks_chat(client):
    owner, donor = _users(client)
    add_hero(client, donor)
    case = add_case(client, owner)
    mid = case["match_id"]
    assert client.get("/api/stats").json() == {"cases_searching": 0, "heroes_available": 1, "cases_success": 0}
    assert client.post(f"/api/matches/{mid}/confirm", headers=donor).status_code == 200
    assert client.get("/api/stats").json()["cases_success"] == 1
    assert client.get("/api/cases").json() == []               # เคสสำเร็จไม่แสดงในรายการเคสด่วน
    assert client.post(f"/api/matches/{mid}/messages", json={"body": "hi"}, headers=owner).status_code == 409
    assert client.post(f"/api/matches/{mid}/confirm", headers=owner).status_code == 409
    assert client.post(f"/api/matches/{mid}/decline", headers=owner).status_code == 409


def test_chat_and_phone_share_go_to_the_right_person(client):
    owner, donor = _users(client)
    add_hero(client, donor)
    mid = add_case(client, owner)["match_id"]
    assert client.post(f"/api/matches/{mid}/messages", json={"body": "  สวัสดีครับ  "}, headers=owner).status_code == 201
    client.post(f"/api/matches/{mid}/share-phone", headers=donor)      # ฮีโร่ส่งเบอร์ของฮีโร่
    client.post(f"/api/matches/{mid}/share-phone", headers=owner)      # เจ้าของเคสส่งเบอร์ของเคส

    view_owner = client.get(f"/api/matches/{mid}", headers=owner).json()
    view_donor = client.get(f"/api/matches/{mid}", headers=donor).json()
    assert view_owner["role"] == "case_owner" and view_donor["role"] == "hero_owner"
    assert [m["body"] for m in view_owner["messages"]] == ["สวัสดีครับ", "0898765432", "0812345678"]
    assert [m["mine"] for m in view_owner["messages"]] == [True, False, True]
    assert [m["mine"] for m in view_donor["messages"]] == [False, True, False]
    assert [m["kind"] for m in view_owner["messages"]] == ["text", "tel", "tel"]
    assert "contact_phone" not in view_owner["hero"] and "contact_phone" not in view_owner["case"]


def test_outsider_cannot_see_or_use_match(client):
    owner, donor = _users(client)
    outsider = make_user(client, "x@example.com", "X")
    add_hero(client, donor)
    mid = add_case(client, owner)["match_id"]
    assert client.get(f"/api/matches/{mid}", headers=outsider).status_code == 404
    assert client.post(f"/api/matches/{mid}/messages", json={"body": "hi"}, headers=outsider).status_code == 404
    assert client.post(f"/api/matches/{mid}/confirm", headers=outsider).status_code == 404
    assert client.get("/api/matches/9999", headers=owner).status_code == 404


def test_blank_message_rejected(client):
    owner, donor = _users(client)
    add_hero(client, donor)
    mid = add_case(client, owner)["match_id"]
    assert client.post(f"/api/matches/{mid}/messages", json={"body": "   "}, headers=owner).status_code == 422


def test_stats_counts(client):
    owner, donor = _users(client)
    assert client.get("/api/stats").json() == {"cases_searching": 0, "heroes_available": 0, "cases_success": 0}
    add_case(client, owner)
    assert client.get("/api/stats").json()["cases_searching"] == 1
