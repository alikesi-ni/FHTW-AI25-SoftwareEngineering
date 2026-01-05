import json
import os
import threading
import time
import pika
from sqlalchemy import select
from app.db import SessionLocal
from app.models import Post
from app.events import publish_event

def _amqp_params() -> pika.ConnectionParameters:
    host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")
    return pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=pika.PlainCredentials(user, password),
    )

def _fetch_post_state(post_id: int) -> dict:
    with SessionLocal() as s:
        p = s.get(Post, post_id)
        if not p:
            return {"post_id": post_id, "status": "FAILED", "error": "post not found"}
        return {
            "post_id": post_id,
            "description_status": getattr(p, "description_status", None),
            "image_description": getattr(p, "image_description", None),
        }

def start_consumer_thread() -> None:
    t = threading.Thread(target=_run, daemon=True)
    t.start()

def _run() -> None:
    queue_name = os.getenv("RABBITMQ_DESCRIBE_RESULTS_QUEUE", "describe_results")

    # wait for rabbitmq
    while True:
        try:
            conn = pika.BlockingConnection(_amqp_params())
            break
        except Exception:
            time.sleep(2)

    ch = conn.channel()
    ch.queue_declare(queue=queue_name, durable=True)
    ch.basic_qos(prefetch_count=10)

    def handle(ch, method, props, body: bytes):
        try:
            msg = json.loads(body.decode("utf-8"))
            post_id = int(msg["post_id"])

            # read canonical state from DB and push to SSE
            event = _fetch_post_state(post_id)
            publish_event(post_id, event)

            ch.basic_ack(method.delivery_tag)
        except Exception:
            # don't loop forever on bad messages
            ch.basic_nack(method.delivery_tag, requeue=False)

    ch.basic_consume(queue=queue_name, on_message_callback=handle)
    ch.start_consuming()
