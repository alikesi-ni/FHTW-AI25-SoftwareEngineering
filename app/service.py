import os
from pathlib import Path
from datetime import datetime
from typing import Optional

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


def add_post(image: Optional[str], comment: Optional[str], username: str) -> int:
    """
    Insert a post enforcing:
    - username is required (non-empty)
    - at least one of (image, comment) must be non-empty
    - if image is given, the file must exist under IMAGE_ROOT
    """

    # Normalize inputs
    username = (username or "").strip()
    image = (image or "").strip() or None
    comment = (comment or "").strip() or None

    if not username:
        raise ValueError("username is required")

    if image is None and comment is None:
        raise ValueError("Either comment or image must be provided")

    # If an image filename is provided, verify the file exists
    if image is not None:
        img_abs = _resolve_under_root(image)
        if not img_abs.exists():
            raise FileNotFoundError(f"Image not found: {img_abs}")

    with _connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO post (image, comment, username, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (image, comment, username, datetime.utcnow()),
        )
        (post_id,) = cur.fetchone()
        return post_id


def get_latest_post():
    posts = get_posts(limit=1)
    if not posts:
        return None
    return posts[0]


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
            (f"%{query}%", f"%{query}%"),
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


def get_posts(
    username: Optional[str] = None,
    order_by: str = "created_at",
    order_dir: str = "desc",
    limit: Optional[int] = None,
):
    # Whitelisted ordering
    order_by_map = {"created_at": "created_at", "id": "id"}
    order_dir_map = {"asc": "ASC", "desc": "DESC"}

    order_col = order_by_map.get(order_by, "created_at")
    order_dir_sql = order_dir_map.get(order_dir.lower(), "DESC")

    base_sql = """
        SELECT id, image, comment, username, created_at
        FROM post
    """

    conditions = []
    params = []

    if username:
        conditions.append("username = %s")
        params.append(username)

    if conditions:
        base_sql += " WHERE " + " AND ".join(conditions)

    base_sql += f" ORDER BY {order_col} {order_dir_sql}"

    if limit is not None:
        base_sql += " LIMIT %s"
        params.append(limit)

    with _connect() as conn, conn.cursor() as cur:
        cur.execute(base_sql, params)
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
