from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel

from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

import app.service as service

import os
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow Angular dev server
    allow_credentials=True,
    allow_methods=["*"],      # VERY IMPORTANT -> OPTIONS is here
    allow_headers=["*"],      # allow Content-Type, etc.
)

# Where to store uploaded images
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}


# Pydantic input model for JSON-based posts (image as string/path/url)
class PostIn(BaseModel):
    image: str
    comment: str
    username: str


@app.post(
    "/posts",
    operation_id="createPostWithImage",
    summary="Create Post With Image",
    description=(
        "Create a post with an uploaded image file (PNG or JPG only).\n\n"
        "Expects multipart/form-data with:\n"
        "- username (form field)\n"
        "- comment  (form field)\n"
        "- image    (file field)\n"
    ),
)
async def create_post_with_image(
    username: str = Form(...),
    comment: str = Form(...),
    image: UploadFile = File(...),
):
    """
    Create a post with an uploaded image file (PNG or JPG only).

    Expects multipart/form-data with:
    - username (form field)
    - comment  (form field)
    - image    (file field)
    """
    # 1) Check content type
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only PNG and JPG images are allowed.",
        )

    # 2) Decide file extension based on content type
    if image.content_type == "image/jpeg":
        ext = ".jpg"
    else:  # image/png
        ext = ".png"

    # 3) Generate a safe, random filename
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # 4) Save file to disk
    try:
        contents = await image.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to save uploaded image.",
        )

    # 5) Use existing add_post function (with filename as param) to save post to db
    try:
        post_id = service.add_post(
            image=filename,
            comment=comment,
            username=username,
        )
        return {"id": post_id, "image_path": file_path}
    except FileNotFoundError as e:
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

