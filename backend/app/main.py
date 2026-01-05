import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.events import router as events_router
from app.routes import router as routes_router
from app.describe_results_consumer import start_consumer_thread


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_consumer_thread()
    yield
    # Shutdown (optional): if you later implement stop/join, call it here.


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    # CORS
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
    app.include_router(events_router)

    return app


app = create_app()
