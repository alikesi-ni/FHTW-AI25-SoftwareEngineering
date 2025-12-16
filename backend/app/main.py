import os
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.routes import router as routes_router


def create_app() -> FastAPI:
    app = FastAPI()

    # CORS (keep as you had it)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static file hosting for uploads
    image_root = os.getenv("IMAGE_ROOT", "uploads")
    os.makedirs(os.path.join(image_root, "original"), exist_ok=True)
    os.makedirs(os.path.join(image_root, "reduced"), exist_ok=True)

    app.mount("/static", StaticFiles(directory=image_root), name="static")

    # Routes
    app.include_router(routes_router)

    return app


app = create_app()
