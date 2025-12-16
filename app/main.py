from typing import Optional, Any

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel

from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

import app.service as service

import os
import uuid

from app import queue

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IMAGE_ROOT = os.getenv("IMAGE_ROOT", "uploads")
ORIGINAL_DIR = os.path.join(IMAGE_ROOT, "original")
REDUCED_DIR = os.path.join(IMAGE_ROOT, "reduced")

os.makedirs(ORIGINAL_DIR, exist_ok=True)
os.makedirs(REDUCED_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=IMAGE_ROOT), name="static")

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}


@app.post(
    "/posts",
    operation_id="createPost",
    summary="Create Post",
    description=(
        "Create a post. Username is required. You must provide at least a comment "
        "or an image (or both).\n\n"
        "Expects multipart/form-data with:\n"
        "- username (form field, required)\n"
        "- comment  (form field, optional)\n"
        "- image    (file field, optional, PNG or JPG only)\n"
    ),
)
async def create_post(
    username: str = Form(...),
    comment: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    """
    Create a post with an optional uploaded image file (PNG or JPG only)
    and/or a text comment.

    Rules:
    - username is required
    - at least one of (comment, image) must be provided
    """
    username = (username or "").strip()
    comment = (comment or "").strip() or None

    if not username:
        raise HTTPException(status_code=400, detail="username is required")

    if comment is None and image is None:
        raise HTTPException(
            status_code=400,
            detail="Either comment or image must be provided.",
        )

    filename: Optional[str] = None
    file_path: Optional[str] = None

    # If an image file was provided, validate + save it
    if image is not None:
        if image.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Only PNG and JPG images are allowed.",
            )

        if image.content_type == "image/jpeg":
            ext = ".jpg"
            # Pillow format would be "JPEG" if you ever process it
        else:  # image/png
            ext = ".png"

        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(ORIGINAL_DIR, filename)

        try:
            contents = await image.read()
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Failed to save uploaded image.",
            )

    # Now store in DB via service layer
    try:
        post_id = service.add_post(
            image_filename=filename,
            comment=comment,
            username=username,
        )

        if filename is not None:
            queue.publish_resize_job(filename)

        response: dict[str, Any] = {"id": post_id}
        # optionally return URLs rather than host paths:
        if filename is not None:
            response["original_url"] = f"/static/original/{filename}"
            # reduced may not exist yet
            response["reduced_url"] = f"/static/reduced/{filename}"
        return response
    except FileNotFoundError as e:
        # Should not happen now since we just saved; but keep it
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/posts/search")
def search(
    q: str = Query(
        ...,
        title="Search Query",
        description="Search string (case-insensitive) used to match comments and usernames.",
    )
):
    try:
        return service.search_posts(q)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/posts")
def get_posts(
    user: Optional[str] = Query(
        None,
        description="Filter posts by exact username",
    ),
    order_by: str = Query(
        "created_at",
        pattern="^(created_at|id)$",
        description="Order by 'created_at' or 'id'",
    ),
    order_dir: str = Query(
        "desc",
        pattern="^(asc|desc)$",
        description="Order direction 'asc' or 'desc'",
    ),
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=1000,
        description="Limit number of returned posts",
    ),
):
    return service.get_posts(
        username=user,
        order_by=order_by,
        order_dir=order_dir,
        limit=limit,
    )

