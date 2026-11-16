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

# ---------------- params 11–18 ----------------
def test_11_path_validation():
    assert client.get("/params/products/5").json() == {"product_id": 5}
    assert client.get("/params/products/1").status_code == 200
    assert client.get("/params/products/10000").status_code == 200
    assert client.get("/params/products/0").status_code == 422
    assert client.get("/params/products/10001").status_code == 422
    assert client.get("/params/products/abc").status_code == 422

def test_12_enum_path():
    assert client.get("/params/category/food").json() == {"category": "food", "is_food": True}
    assert client.get("/params/category/books").json() == {"category": "books", "is_food": False}
    assert client.get("/params/category/toys").status_code == 422

def test_13_path_converter():
    assert client.get("/params/files/a/b/c.txt").json() == {"file_path": "a/b/c.txt"}
    assert client.get("/params/files/readme.md").json() == {"file_path": "readme.md"}

def test_14_query_params():
    r = client.get("/params/search", params={"q": "x"})
    assert r.json() == {"q": "x", "page": 1, "active": False, "sort": None}
    assert client.get("/params/search").status_code == 422  # q required
    for truthy in ["yes", "true", "1", "on"]:
        assert client.get("/params/search", params={"q": "x", "active": truthy}).json()["active"] is True
    assert client.get("/params/search", params={"q": "x", "page": "abc"}).status_code == 422
    assert client.get("/params/search", params={"q": "x", "active": "maybe"}).status_code == 422

def test_15_query_validation_alias():
    assert client.get("/params/validate").json() == {"q": None, "item_query": None, "old": None}
    assert client.get("/params/validate", params={"q": "hello"}).json()["q"] == "hello"
    assert client.get("/params/validate", params={"q": "ab"}).status_code == 422        # too short
    assert client.get("/params/validate", params={"q": "a" * 21}).status_code == 422    # too long
    assert client.get("/params/validate", params={"q": "abc123"}).status_code == 422    # regex
    assert client.get("/params/validate", params={"item-query": "foo"}).json()["item_query"] == "foo"
    assert client.get("/params/validate", params={"item_query": "foo"}).json()["item_query"] is None  # alias only

def test_16_list_uuid_datetime():
    assert client.get("/params/multi").json() == {"tags": [], "request_id": None, "since": None}
    r = client.get("/params/multi?tag=a&tag=b")
    assert r.json()["tags"] == ["a", "b"]
    uid = "12345678-1234-5678-1234-567812345678"
    assert client.get("/params/multi", params={"request_id": uid}).json()["request_id"] == uid
    assert client.get("/params/multi", params={"request_id": "nope"}).status_code == 422
    r = client.get("/params/multi", params={"since": "2024-01-02T03:04:05"})
    assert r.json()["since"] == "2024-01-02T03:04:05"
    assert client.get("/params/multi", params={"since": "yesterday"}).status_code == 422

def test_17_headers_cookies():
    r = client.get("/params/meta", headers={"User-Agent": "pytest-ua", "X-Token": "t1"}, cookies={"session_id": "abc"})
    body = r.json()
    assert body["user_agent"] == "pytest-ua"
    assert body["x_token"] == ["t1"]
    assert body["session_id"] == "abc"
    r = client.get("/params/meta", headers=[("X-Token", "a"), ("X-Token", "b")])
    assert r.json()["x_token"] == ["a", "b"]
    assert client.get("/params/meta").json()["session_id"] is None

def test_18_raw_request():
    r = client.get("/params/raw?x=1&y=2")
    body = r.json()
    assert body["method"] == "GET"
    assert body["query"] == {"x": "1", "y": "2"}
    assert body["url"].endswith("/params/raw?x=1&y=2")
    assert body["client"] is not None


# ---------------- bodies 19–20 ----------------
ITEM = {"name": "Keyboard", "price": 100, "category": "electronics", "tags": ["usb"]}

def test_19_create_item():
    r = client.post("/bodies/items", json=ITEM)
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Keyboard"
    assert body["price_with_tax"] == 108.0
    assert body["category"] == "electronics"

def test_19_defaults():
    r = client.post("/bodies/items", json={"name": "Novel", "price": 9.99})
    assert r.status_code == 201
    assert r.json()["category"] == "books" and r.json()["tags"] == []

def test_19_validation_errors():
    assert client.post("/bodies/items", json={**ITEM, "price": 0}).status_code == 422
    assert client.post("/bodies/items", json={**ITEM, "price": -5}).status_code == 422
    assert client.post("/bodies/items", json={**ITEM, "name": ""}).status_code == 422
    assert client.post("/bodies/items", json={**ITEM, "name": "x" * 51}).status_code == 422
    assert client.post("/bodies/items", json={**ITEM, "category": "toys"}).status_code == 422
    assert client.post("/bodies/items", json={"name": "NoPrice"}).status_code == 422
    assert client.post("/bodies/items").status_code == 422

def test_20_body_path_query():
    r = client.put("/bodies/items/7?notify=true", json=ITEM)
    assert r.status_code == 200
    body = r.json()
    assert body["item_id"] == 7 and body["notify"] is True
    assert body["item"]["name"] == "Keyboard"
    assert client.put("/bodies/items/7", json=ITEM).json()["notify"] is False
    assert client.put("/bodies/items/abc", json=ITEM).status_code == 422
    assert client.put("/bodies/items/7", json={"name": "x"}).status_code == 422
