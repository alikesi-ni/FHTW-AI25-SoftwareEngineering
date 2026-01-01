# tests/conftest.py
import os
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.main import app  # FastAPI instance

BACKEND_ROOT = Path(__file__).resolve().parents[1]          # .../backend
REPO_ROOT = BACKEND_ROOT.parent                             # repo root
UPLOADS_DIR = REPO_ROOT / "uploads"                         # repo-level uploads
ORIGINAL_DIR = UPLOADS_DIR / "original"
REDUCED_DIR = UPLOADS_DIR / "reduced"


def _connect():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "social"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "password"),
    )


# Must match your current db/init.sql schema (at least columns used by tests)
POST_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS post (
  id                  SERIAL PRIMARY KEY,
  image_filename      TEXT,
  image_status        TEXT NOT NULL DEFAULT 'READY',
  image_description   TEXT,
  description_status  TEXT NOT NULL DEFAULT 'NONE',
  content             TEXT,
  username            TEXT NOT NULL,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT post_content_or_image
    CHECK (content IS NOT NULL OR image_filename IS NOT NULL),

  CONSTRAINT post_content_length
    CHECK (content IS NULL OR char_length(content) <= 280),

  CONSTRAINT post_image_status
    CHECK (
      (image_filename IS NULL AND image_status = 'READY')
      OR
      (image_filename IS NOT NULL AND image_status IN ('PENDING', 'READY', 'FAILED'))
    ),

  CONSTRAINT post_description_status
    CHECK (
      (image_filename IS NULL AND description_status = 'NONE')
      OR
      (image_filename IS NOT NULL AND description_status IN ('NONE', 'PENDING', 'READY', 'FAILED'))
    )
);
"""


@pytest.fixture(autouse=True)
def setup_db_and_env(monkeypatch):
    """
    - Point IMAGE_ROOT to the repo's uploads folder
    - Ensure the 'post' table exists (same as db/init.sql)
    - Truncate it before each test
    - Ensure uploads/original and uploads/reduced exist
    """
    monkeypatch.setenv("IMAGE_ROOT", str(UPLOADS_DIR))

    ORIGINAL_DIR.mkdir(parents=True, exist_ok=True)
    REDUCED_DIR.mkdir(parents=True, exist_ok=True)

    with _connect() as conn, conn.cursor() as cur:
        cur.execute(POST_TABLE_SQL)
        conn.commit()

        cur.execute("TRUNCATE TABLE post RESTART IDENTITY;")
        conn.commit()

    yield


@pytest.fixture
def client():
    return TestClient(app)
