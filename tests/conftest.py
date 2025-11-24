# tests/conftest.py
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.service import _connect


@pytest.fixture(autouse=True)
def clear_db():
    """
    Automatically truncate the post table before each test.
    Uses the same connection settings as the app.
    """
    with _connect() as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE post RESTART IDENTITY CASCADE;")
        conn.commit()
    yield


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)
