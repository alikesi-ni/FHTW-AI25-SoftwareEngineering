import pytest

import app.service as service


@pytest.fixture
def sample_posts(tmp_path):
    """
    Insert three sample posts using existing image files:

      charmander.png - alice
      bulbasaur.png  - bob
      squirtle.png   - carol

    Assumes these files exist under IMAGE_ROOT/original.
    """
    id1 = service.add_post(
        image_filename="charmander.png",
        content="First post!",
        username="alice",
    )
    id2 = service.add_post(
        image_filename="bulbasaur.png",
        content="Leafy vibes 🍃",
        username="bob",
    )
    id3 = service.add_post(
        image_filename="squirtle.png",
        content="Stay hydrated 💧",
        username="carol",
    )
    return [id1, id2, id3]


def test_get_posts_empty_returns_empty_list():
    posts = service.get_posts()
    assert posts == []


def test_get_posts_ordering_with_sample_posts(sample_posts):
    posts = service.get_posts(order_by="created_at", order_dir="desc")

    assert len(posts) == 3
    ids = [p["id"] for p in posts]

    id1, id2, id3 = sample_posts
    assert ids == [id3, id2, id1]


def test_get_posts_filter_by_username(sample_posts):
    posts = service.get_posts(username="alice", order_by="id", order_dir="asc")

    assert len(posts) == 1
    assert posts[0]["username"] == "alice"
    assert posts[0]["image_filename"] == "charmander.png"
    assert posts[0]["content"] == "First post!"
    assert posts[0]["image_status"] == "PENDING"


def test_get_latest_post_returns_none_when_no_posts():
    latest = service.get_latest_post()
    assert latest is None


def test_get_latest_post_returns_latest_post(sample_posts):
    _, _, id3 = sample_posts

    latest = service.get_latest_post()
    assert latest is not None
    assert latest["id"] == id3
    assert latest["content"] == "Stay hydrated 💧"
    assert latest["username"] == "carol"


def test_add_post_requires_username():
    with pytest.raises(ValueError):
        service.add_post(image_filename=None, content="hello", username="")


def test_add_post_requires_content_or_image():
    with pytest.raises(ValueError):
        service.add_post(image_filename=None, content=None, username="alice")
