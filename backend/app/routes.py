import os
import uuid
from typing import Optional, Any, List

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query

import app.service as service
from app import queue
from app.schemas import PostOut

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}


@router.post(
    "/posts",
    operation_id="createPost",
    summary="Create Post",
    description=(
        "Create a post. Username is required. You must provide at least content "
        "or an image (or both).\n\n"
        "Expects multipart/form-data with:\n"
        "- username (form field, required)\n"
        "- content  (form field, optional)\n"
        "- image    (file field, optional, PNG or JPG only)\n"
    ),
)
async def create_post(
    username: str = Form(...),
    content: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    username = (username or "").strip()
    content = (content or "").strip() or None

    if not username:
        raise HTTPException(status_code=400, detail="username is required")

    if content is None and image is None:
        raise HTTPException(status_code=400, detail="Either content or image must be provided.")

    filename: Optional[str] = None

    if image is not None:
        if image.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=400, detail="Only PNG and JPG images are allowed.")

        ext = ".jpg" if image.content_type == "image/jpeg" else ".png"
        filename = f"{uuid.uuid4().hex}{ext}"

        image_root = os.getenv("IMAGE_ROOT", "uploads")
        original_dir = os.path.join(image_root, "original")
        file_path = os.path.join(original_dir, filename)

        try:
            contents = await image.read()
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to save uploaded image.")

    try:
        post_id = service.add_post(
            image_filename=filename,
            content=content,
            username=username,
        )

        if filename is not None:
            queue.publish_resize_job(filename)

        response: dict[str, Any] = {"id": post_id}
        if filename is not None:
            response["original_url"] = f"/static/original/{filename}"
            response["reduced_url"] = f"/static/reduced/{filename}"
        return response

    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/posts/search", response_model=List[PostOut])
def search_posts(
    q: str = Query(..., title="Search Query", description="Search in post content and usernames"),
):
    try:
        return service.search_posts(q)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/posts", response_model=List[PostOut])
def get_posts(
    user: Optional[str] = Query(None, description="Filter posts by exact username"),
    order_by: str = Query("created_at", pattern="^(created_at|id)$"),
    order_dir: str = Query("desc", pattern="^(asc|desc)$"),
    limit: Optional[int] = Query(None, ge=1, le=1000),
):
    return service.get_posts(username=user, order_by=order_by, order_dir=order_dir, limit=limit)


@router.get("/posts/{post_id}", response_model=PostOut)
def get_post(post_id: int):
    post = service.get_post_by_id(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/posts/{post_id}/describe", status_code=202)
def describe_post(post_id: int):
    try:
        post = service.get_post_by_id(post_id)
        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        if not post.get("image_filename"):
            raise HTTPException(status_code=400, detail="Post has no image")

        # If already ready, return immediately
        if post.get("image_description"):
            return {"status": "READY"}

        service.mark_description_pending(post_id)
        queue.publish_describe_job(post_id, post["image_filename"])
        return {"status": "PENDING"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
