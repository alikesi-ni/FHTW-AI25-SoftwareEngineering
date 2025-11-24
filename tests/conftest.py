# tests/conftest.py
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.service import _connect

REPO_ROOT = Path(__file__).resolve().parents[1]
UPLOADS_DIR = REPO_ROOT / "uploads"

# Must match db/init.sql
POST_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS post (
  id         SERIAL PRIMARY KEY,
  image      TEXT,
  comment    TEXT,
  username   TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT post_comment_or_image
    CHECK (comment IS NOT NULL OR image IS NOT NULL)
);
"""


@pytest.fixture(autouse=True)
def setup_db_and_env(monkeypatch):
    """
    - Point IMAGE_ROOT to the repo's uploads folder
    - Ensure the 'post' table exists (same as db/init.sql)
    - Truncate it before each test
    """
    # Ensure service._image_root() uses the repo uploads dir
    monkeypatch.setenv("IMAGE_ROOT", str(UPLOADS_DIR))

    with _connect() as conn, conn.cursor() as cur:
        # 1) Ensure the table exists (no-op if already created by init.sql)
        cur.execute(POST_TABLE_SQL)
        conn.commit()

        # 2) Clear the table before each test
        cur.execute("TRUNCATE TABLE post RESTART IDENTITY;")
        conn.commit()

    yield


@pytest.fixture
def client():
    """FastAPI test client for API tests."""
    return TestClient(app)
