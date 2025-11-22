import os
from pathlib import Path
from datetime import datetime
import psycopg

def _connect():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "social"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "password"),
    )

def _image_root() -> Path:
    root = Path(os.getenv("IMAGE_ROOT", "uploads"))
    root.mkdir(parents=True, exist_ok=True)
    return root

def _resolve_under_root(image_rel: str) -> Path:
    root = _image_root().resolve()
    p = (root / image_rel).resolve()
    if root not in p.parents and p != root:
        raise ValueError("image path must be inside IMAGE_ROOT")
    return p

def add_post(image: str, comment: str, username: str) -> int:
    """Insert a post after verifying the image file exists under IMAGE_ROOT."""
    if not (image and comment and username):
        raise ValueError("image, comment, and username are required")

    img_abs = _resolve_under_root(image)
    if not img_abs.exists():
        raise FileNotFoundError(f"Image not found: {img_abs}")

    with _connect() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO post (image, comment, username, created_at) "
            "VALUES (%s,%s,%s,%s) RETURNING id",
            (image, comment, username, datetime.utcnow()),
        )
        (post_id,) = cur.fetchone()
        return post_id

def get_latest_post():
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, image, comment, username, created_at "
            "FROM post ORDER BY created_at DESC, id DESC LIMIT 1"
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0], "image": row[1], "comment": row[2],
            "username": row[3], "created_at": row[4],
        }

def search_posts(query: str):
    """Search for posts where the comment or username contains the query."""
    if not query:
        raise ValueError("Search query cannot be empty")

    with _connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, image, comment, username, created_at
            FROM post
            WHERE comment ILIKE %s
               OR username ILIKE %s
            ORDER BY created_at DESC, id DESC;
            """,
            (f"%{query}%", f"%{query}%")
        )
        rows = cur.fetchall()

        return [
            {
                "id": r[0],
                "image": r[1],
                "comment": r[2],
                "username": r[3],
                "created_at": r[4],
            }
            for r in rows
        ]

def get_post_by_id(post_id: int):
    """Return a post with the given ID, or None if not found."""
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, image, comment, username, created_at
            FROM post
            WHERE id = %s
            """,
            (post_id,)
        )
        row = cur.fetchone()
        if not row:
            return None

        return {
            "id": row[0],
            "image": row[1],
            "comment": row[2],
            "username": row[3],
            "created_at": row[4],
        }
