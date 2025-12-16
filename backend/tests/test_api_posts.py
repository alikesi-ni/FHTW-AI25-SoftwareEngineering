import io
from typing import Dict

from fastapi.testclient import TestClient


def create_content_only_post(client: TestClient, username: str, content: str) -> Dict:
    resp = client.post(
        "/posts",
        data={"username": username, "content": content},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "id" in body
    return body


def test_get_posts_initially_empty(client: TestClient):
    resp = client.get("/posts")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_post_content_only_via_api(client: TestClient):
    body = create_content_only_post(client, "alice", "hello world")

    list_resp = client.get("/posts")
    assert list_resp.status_code == 200
    posts = list_resp.json()

    assert len(posts) == 1
    assert posts[0]["id"] == body["id"]
    assert posts[0]["username"] == "alice"
    assert posts[0]["content"] == "hello world"
    assert posts[0]["image_filename"] is None
    assert posts[0]["image_status"] == "READY"


def test_create_post_with_image_via_api(client: TestClient, monkeypatch):
    # Mock RabbitMQ publisher so tests don't require a running RabbitMQ
    monkeypatch.setattr("app.queue.publish_resize_job", lambda filename: None)

    # Minimal valid PNG (1x1)
    tiny_png = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01\xe2!\xbc3"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    files = {"image": ("test.png", io.BytesIO(tiny_png), "image/png")}
    data = {"username": "bob", "content": "with image"}

    resp = client.post("/posts", data=data, files=files)
    assert resp.status_code == 200
    body = resp.json()
    assert "id" in body

    list_resp = client.get("/posts")
    assert list_resp.status_code == 200
    posts = list_resp.json()
    assert len(posts) == 1

    assert posts[0]["username"] == "bob"
    assert posts[0]["content"] == "with image"
    assert posts[0]["image_filename"] is not None
    assert posts[0]["image_status"] == "PENDING"


def test_create_post_requires_username(client: TestClient):
    resp = client.post("/posts", data={"username": "", "content": "hi"})
    assert resp.status_code == 400
    assert "username is required" in resp.json()["detail"]


def test_create_post_requires_content_or_image(client: TestClient):
    resp = client.post("/posts", data={"username": "alice", "content": ""})
    assert resp.status_code == 400
    assert "Either content or image must be provided" in resp.json()["detail"]


def test_get_posts_filter_by_user(client: TestClient):
    create_content_only_post(client, "alice", "a1")
    create_content_only_post(client, "bob", "b1")
    create_content_only_post(client, "alice", "a2")

    resp = client.get(
        "/posts",
        params={"user": "alice", "order_by": "id", "order_dir": "asc"},
    )
    assert resp.status_code == 200
    posts = resp.json()

    assert len(posts) == 2
    assert [p["username"] for p in posts] == ["alice", "alice"]


def test_get_latest_via_posts_limit(client: TestClient):
    resp = client.get("/posts", params={"limit": 1})
    assert resp.status_code == 200
    assert resp.json() == []

    create_content_only_post(client, "alice", "first")
    body2 = create_content_only_post(client, "alice", "second")

    resp2 = client.get(
        "/posts",
        params={"limit": 1, "order_by": "created_at", "order_dir": "desc"},
    )
    assert resp2.status_code == 200
    posts = resp2.json()

    assert len(posts) == 1
    assert posts[0]["id"] == body2["id"]
    assert posts[0]["content"] == "second"
    assert posts[0]["username"] == "alice"


def test_search_posts_endpoint(client: TestClient):
    create_content_only_post(client, "alice", "hello world")
    create_content_only_post(client, "bob", "something else")

    resp = client.get("/posts/search", params={"q": "hello"})
    assert resp.status_code == 200
    results = resp.json()

    assert len(results) == 1
    assert results[0]["username"] == "alice"
    assert "hello" in results[0]["content"].lower()
