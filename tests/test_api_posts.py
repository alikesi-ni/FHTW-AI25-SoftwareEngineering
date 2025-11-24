import io
from typing import Dict

from fastapi.testclient import TestClient


def create_comment_only_post(client: TestClient, username: str, comment: str) -> Dict:
    resp = client.post(
        "/posts",
        data={"username": username, "comment": comment},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "id" in body
    return body


def test_get_posts_initially_empty(client: TestClient):
    resp = client.get("/posts")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_post_comment_only_via_api(client: TestClient):
    body = create_comment_only_post(client, "alice", "hello world")

    list_resp = client.get("/posts")
    assert list_resp.status_code == 200
    posts = list_resp.json()

    assert len(posts) == 1
    assert posts[0]["id"] == body["id"]
    assert posts[0]["username"] == "alice"
    assert posts[0]["comment"] == "hello world"
    # image may be null or empty depending on service implementation
    assert posts[0]["image"] is None or posts[0]["image"] == ""


def test_create_post_with_image_via_api(client: TestClient):
    # Fake PNG bytes
    fake_image_bytes = b"\x89PNG\r\n\x1a\n" + b"fakepngdata"

    files = {
        "image": ("test.png", io.BytesIO(fake_image_bytes), "image/png")
    }
    data = {
        "username": "bob",
        "comment": "with image",
    }

    resp = client.post("/posts", data=data, files=files)
    assert resp.status_code == 200
    body = resp.json()
    assert "id" in body

    # Check it's visible in /posts
    list_resp = client.get("/posts")
    assert list_resp.status_code == 200
    posts = list_resp.json()
    assert len(posts) == 1
    assert posts[0]["username"] == "bob"
    assert posts[0]["comment"] == "with image"
    assert posts[0]["image"] is not None


def test_create_post_requires_username(client: TestClient):
    resp = client.post("/posts", data={"username": "", "comment": "hi"})
    assert resp.status_code == 400
    assert "username is required" in resp.json()["detail"]


def test_create_post_requires_comment_or_image(client: TestClient):
    # No comment, no image -> should fail
    resp = client.post("/posts", data={"username": "alice", "comment": ""})
    assert resp.status_code == 400
    assert "Either comment or image must be provided" in resp.json()["detail"]


def test_get_posts_filter_by_user(client: TestClient):
    create_comment_only_post(client, "alice", "a1")
    create_comment_only_post(client, "bob", "b1")
    create_comment_only_post(client, "alice", "a2")

    resp = client.get(
        "/posts",
        params={
            "user": "alice",
            "order_by": "id",
            "order_dir": "asc",
        },
    )
    assert resp.status_code == 200
    posts = resp.json()

    assert len(posts) == 2
    assert [p["username"] for p in posts] == ["alice", "alice"]


def test_get_latest_via_posts_limit(client: TestClient):
    # Initially: no posts -> /posts?limit=1 returns empty list
    resp = client.get("/posts", params={"limit": 1})
    assert resp.status_code == 200
    assert resp.json() == []

    # After creating posts
    create_comment_only_post(client, "alice", "first")
    body2 = create_comment_only_post(client, "alice", "second")

    resp2 = client.get(
        "/posts",
        params={
            "limit": 1,
            "order_by": "created_at",
            "order_dir": "desc",
        },
    )
    assert resp2.status_code == 200
    posts = resp2.json()
    assert len(posts) == 1
    assert posts[0]["id"] == body2["id"]
    assert posts[0]["comment"] == "second"
    assert posts[0]["username"] == "alice"


def test_search_posts_endpoint(client: TestClient):
    create_comment_only_post(client, "alice", "hello world")
    create_comment_only_post(client, "bob", "something else")

    resp = client.get("/posts/search", params={"q": "hello"})
    assert resp.status_code == 200
    results = resp.json()

    assert len(results) == 1
    assert results[0]["username"] == "alice"
    assert "hello" in results[0]["comment"].lower()
