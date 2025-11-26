import pytest

import app.service as service


@pytest.fixture
def sample_posts():
  """
  Insert three sample posts using existing image files:

    charmander.png - alice
    bulbasaur.png  - bob
    squirtle.png   - carol

  Assumes these files exist under IMAGE_ROOT (default: ./uploads).
  """
  id1 = service.add_post(
      image="charmander.png",
      comment="First post!",
      username="alice",
  )
  id2 = service.add_post(
      image="bulbasaur.png",
      comment="Leafy vibes 🍃",
      username="bob",
  )
  id3 = service.add_post(
      image="squirtle.png",
      comment="Stay hydrated 💧",
      username="carol",
  )
  return [id1, id2, id3]


def test_get_posts_empty_returns_empty_list():
  posts = service.get_posts()
  assert posts == []


def test_get_posts_ordering_with_sample_posts(sample_posts):
  # When ordered by created_at desc, the last inserted should come first
  posts = service.get_posts(order_by="created_at", order_dir="desc")

  assert len(posts) == 3
  ids = [p["id"] for p in posts]

  # sample_posts = [id1, id2, id3] in insertion order
  id1, id2, id3 = sample_posts

  # Newest (id3) first, then id2, then id1
  assert ids == [id3, id2, id1]


def test_get_posts_filter_by_username(sample_posts):
  # Filter only alice's posts
  posts = service.get_posts(username="alice", order_by="id", order_dir="asc")

  assert len(posts) == 1
  assert posts[0]["username"] == "alice"
  assert posts[0]["image"] == "charmander.png"
  assert posts[0]["comment"] == "First post!"


def test_get_latest_post_returns_none_when_no_posts():
  latest = service.get_latest_post()
  assert latest is None


def test_get_latest_post_returns_latest_post(sample_posts):
  id1, id2, id3 = sample_posts

  latest = service.get_latest_post()
  assert latest is not None
  assert latest["id"] == id3
  assert latest["comment"] == "Stay hydrated 💧"
  assert latest["username"] == "carol"


def test_add_post_requires_username():
  with pytest.raises(ValueError):
    service.add_post(image=None, comment="hello", username="")


def test_add_post_requires_comment_or_image():
  # Both comment and image empty -> ValueError
  with pytest.raises(ValueError):
    service.add_post(image=None, comment=None, username="alice")
