# tests/conftest.py
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.service import _connect

REPO_ROOT = Path(__file__).resolve().parents[1]
UPLOADS_DIR = REPO_ROOT / "uploads"
INIT_SQL_PATH = REPO_ROOT / "db" / "init.sql"


@pytest.fixture(autouse=True)
def setup_db_and_env(monkeypatch):
    """
    - Point IMAGE_ROOT to the repo's uploads folder
    - Ensure the schema from db/init.sql is applied
    - Truncate table 'post' before each test
    """
    # Ensure service._image_root() uses the repo uploads dir
    monkeypatch.setenv("IMAGE_ROOT", str(UPLOADS_DIR))

    # Load the same SQL the containers use
    init_sql = INIT_SQL_PATH.read_text(encoding="utf-8")

    with _connect() as conn, conn.cursor() as cur:
        # 1) Apply init.sql (idempotent CREATE TABLE IF NOT EXISTS ...)
        cur.execute(init_sql)
        conn.commit()

        # 2) Clear the table for a clean state in each test
        cur.execute("TRUNCATE TABLE post RESTART IDENTITY;")
        conn.commit()

    yield


@pytest.fixture
def client():
    """FastAPI test client for API tests."""
    return TestClient(app)
