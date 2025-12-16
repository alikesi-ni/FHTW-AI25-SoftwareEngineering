import os
from pathlib import Path
from typing import Optional

from sqlalchemy import select, or_

from app.db import SessionLocal
from app.models import Post


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


def add_post(image_filename: Optional[str], content: Optional[str], username: str) -> int:
    username = (username or "").strip()
    image_filename = (image_filename or "").strip() or None
    content = (content or "").strip() or None

    if not username:
        raise ValueError("username is required")

    if image_filename is None and content is None:
        raise ValueError("Either content or image_filename must be provided")

    if image_filename is not None:
        img_abs = _resolve_under_root(f"original/{image_filename}")
        if not img_abs.exists():
            raise FileNotFoundError(f"Image not found: {img_abs}")

    image_status = "PENDING" if image_filename is not None else "READY"

    with SessionLocal() as db:
        post = Post(
            image_filename=image_filename,
            image_status=image_status,
            content=content,
            username=username,
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        return post.id


def get_latest_post():
    posts = get_posts(limit=1, order_by="created_at", order_dir="desc")
    return posts[0] if posts else None


def search_posts(query: str):
    if not query:
        raise ValueError("Search query cannot be empty")

    q = f"%{query}%"

    stmt = (
        select(Post)
        .where(or_(Post.content.ilike(q), Post.username.ilike(q)))
        .order_by(Post.created_at.desc(), Post.id.desc())
    )

    with SessionLocal() as db:
        rows = db.execute(stmt).scalars().all()
        return [_to_dict(p) for p in rows]


def get_posts(
    username: Optional[str] = None,
    order_by: str = "created_at",
    order_dir: str = "desc",
    limit: Optional[int] = None,
):
    order_by_map = {"created_at": Post.created_at, "id": Post.id}
    col = order_by_map.get(order_by, Post.created_at)
    col = col.asc() if order_dir.lower() == "asc" else col.desc()

    stmt = select(Post)

    if username:
        stmt = stmt.where(Post.username == username)

    # stable ordering (matches your old SQL behavior)
    stmt = stmt.order_by(col, Post.id.asc() if order_dir.lower() == "asc" else Post.id.desc())

    if limit is not None:
        stmt = stmt.limit(limit)

    with SessionLocal() as db:
        rows = db.execute(stmt).scalars().all()
        return [_to_dict(p) for p in rows]


def _to_dict(p: Post) -> dict:
    return {
        "id": p.id,
        "image_filename": p.image_filename,
        "image_status": p.image_status,
        "content": p.content,
        "username": p.username,
        "created_at": p.created_at,
    }
