import asyncio
import json
from collections import defaultdict
from typing import AsyncGenerator
from fastapi import APIRouter
from starlette.responses import StreamingResponse

router = APIRouter()

_subscribers: dict[int, list[asyncio.Queue[dict]]] = defaultdict(list)

def publish_event(post_id: int, event: dict) -> None:
    # Called from backend result-consumer thread
    queues = list(_subscribers.get(post_id, []))
    for q in queues:
        try:
            q.put_nowait(event)
        except Exception:
            pass

@router.get("/events/posts/{post_id}")
async def sse_post_events(post_id: int):
    q: asyncio.Queue[dict] = asyncio.Queue()
    _subscribers[post_id].append(q)

    async def gen() -> AsyncGenerator[bytes, None]:
        try:
            # initial hello to establish stream
            yield b"event: ready\ndata: {}\n\n"
            while True:
                event = await q.get()
                payload = json.dumps(event)
                yield f"event: description\ndata: {payload}\n\n".encode("utf-8")
        finally:
            _subscribers[post_id].remove(q)
            if not _subscribers[post_id]:
                _subscribers.pop(post_id, None)

    return StreamingResponse(gen(), media_type="text/event-stream")
