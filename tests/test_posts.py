import os
from pathlib import Path
import psycopg
import pytest

from app.service import add_post, get_latest_post

REPO_ROOT = Path(__file__).resolve().parents[1]
UPLOADS_DIR = REPO_ROOT / "uploads"

def _conn():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "social"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "password"),
    )

@pytest.fixture(autouse=True)
def setup_db_and_env(monkeypatch):
    # Point the app to the repo uploads folder so image checks work
    monkeypatch.setenv("IMAGE_ROOT", str(UPLOADS_DIR))

    # Clean the table before each test
    with _conn() as c, c.cursor() as cur:
        cur.execute("TRUNCATE post RESTART IDENTITY;")
    yield

def test_insert_three_and_latest():
    # images must exist in uploads/ in the repo
    for name in ("charmander.png", "bulbasaur.png", "squirtle.png"):
        assert (UPLOADS_DIR / name).exists(), f"Missing image: {name}"

    add_post("charmander.png", "First post!", "alice")
    add_post("bulbasaur.png",  "Leafy vibes 🍃", "bob")
    add_post("squirtle.png",   "Stay hydrated 💧", "carol")

    latest = get_latest_post()
    assert latest is not None
    assert latest["image"] == "squirtle.png"
    assert latest["comment"] == "Stay hydrated 💧"
    assert latest["username"] == "carol"

def test_missing_image_raises():
    with pytest.raises(FileNotFoundError):
        add_post("does_not_exist.png", "text", "user")
