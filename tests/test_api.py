from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------- basics 01–08 ----------------
def test_01_root():
    assert client.get("/").json() == {"message": "Hello, FastAPI"}

def test_02_async():
    assert client.get("/async-hello").status_code == 200

def test_03_health():
    assert client.get("/health").json()["status"] == "ok"

def test_04_methods():
    for m in ["get", "post", "put", "patch", "delete"]:
        r = getattr(client, m)("/methods")
        assert r.status_code == 200 and r.headers["X-Handled-By"] == "api_route"

def test_05_created():
    r = client.post("/created")
    assert r.status_code == 201
    assert r.headers["Location"] == "/items/1"
    assert "session_hint" in r.cookies

def test_06_custom_json():
    r = client.get("/custom-json")
    assert r.status_code == 202 and r.headers["X-Custom"] == "yes"

def test_07_text_html():
    assert client.get("/text").text == "Just Text"
    assert "<h1>" in client.get("/html").text

def test_08_redirect_and_204():
    r = client.get("/old-path", follow_redirects=False)
    assert r.status_code == 308
    r = client.get("/no-content")
    assert r.status_code == 204 and r.content == b""


# ---------------- params 09–10 ----------------
def test_09_path_int():
    assert client.get("/params/users/7").json() == {"user_id": 7}
    assert client.get("/params/users/abc").status_code == 422

def test_10_route_order():
    assert client.get("/params/profiles/me").json() == {"profile": "current user"}
    assert client.get("/params/profiles/sam").json() == {"profile": "sam"}