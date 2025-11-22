from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.service import add_post, get_latest_post
from app.service import search_posts
from app.service import get_post_by_id

app = FastAPI()

# Pydantic input model
class PostIn(BaseModel):
    image: str
    comment: str
    username: str


@app.post("/posts")
def create_post_api(data: PostIn):
    try:
        post_id = add_post(
            image=data.image,
            comment=data.comment,
            username=data.username,
        )
        return {"id": post_id}
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/posts/latest")
def get_latest():
    post = get_latest_post()
    if not post:
        raise HTTPException(status_code=404, detail="No posts found.")
    return post


@app.get("/posts/search")
def search(q: str):
    try:
        return search_posts(q)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    post = get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
