from tests.conftest import PNG, make_user


def test_upload_png_then_public_download(client):
    h = make_user(client)
    r = client.post("/api/uploads", files={"file": ("a.png", PNG, "image/png")}, headers=h)
    assert r.status_code == 201
    url = r.json()["url"]
    got = client.get(url)                                       # รูปเปิดดูได้โดยไม่ต้องล็อกอิน
    assert got.status_code == 200 and got.headers["content-type"] == "image/png" and got.content == PNG
    assert got.headers["x-content-type-options"] == "nosniff"


def test_upload_requires_login(client):
    assert client.post("/api/uploads", files={"file": ("a.png", PNG, "image/png")}).status_code == 401


def test_rejects_non_image_even_if_named_png(client):
    h = make_user(client)
    r = client.post("/api/uploads", files={"file": ("evil.png", b"<script>alert(1)</script>", "image/png")}, headers=h)
    assert r.status_code == 415


def test_rejects_oversize(client):
    h = make_user(client)
    big = PNG + b"0" * (2 * 1024 * 1024)
    assert client.post("/api/uploads", files={"file": ("big.png", big, "image/png")}, headers=h).status_code == 413


def test_path_traversal_and_unknown_names_404(client):
    assert client.get("/api/uploads/..%2Fsecret.png").status_code == 404
    assert client.get("/api/uploads/" + "0" * 32 + ".png").status_code == 404


def test_photo_url_must_be_our_own_upload(client):
    from tests.conftest import case_payload
    h = make_user(client)
    r = client.post("/api/cases", json=case_payload(photo_url="https://evil.example/x.png"), headers=h)
    assert r.status_code == 422
