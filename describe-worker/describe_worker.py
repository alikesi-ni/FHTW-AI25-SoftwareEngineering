import base64
import json
import os
import time
from pathlib import Path
from typing import Optional

import httpx
import pika
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def amqp_params() -> pika.ConnectionParameters:
    host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")
    credentials = pika.PlainCredentials(user, password)
    return pika.ConnectionParameters(host=host, port=port, credentials=credentials)


def db_url() -> str:
    host = os.getenv("DB_HOST", "db")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "social")
    user = os.getenv("DB_USER", "admin")
    pw = os.getenv("DB_PASSWORD", "password")
    return f"postgresql+psycopg://{user}:{pw}@{host}:{port}/{name}"


def make_engine() -> Engine:
    return create_engine(db_url(), pool_pre_ping=True)


def wait_for_db(engine: Engine) -> None:
    while True:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception as e:
            print(f"[describe-worker] DB not ready yet: {e}. Retrying...")
            time.sleep(2)


def wait_for_rabbitmq() -> pika.BlockingConnection:
    while True:
        try:
            return pika.BlockingConnection(amqp_params())
        except Exception as e:
            print(f"[describe-worker] RabbitMQ not ready yet: {e}. Retrying...")
            time.sleep(2)


def mime_from_filename(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext in (".jpg", ".jpeg"):
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    # fallback; Gemini usually still works, but better to be explicit
    return "application/octet-stream"


def gemini_caption(image_bytes: bytes, mime_type: str, prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{model}:generateContent"
    )

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "contents": [
            {
                "parts": [
                    {"inlineData": {"mimeType": mime_type, "data": image_b64}},
                    {"text": prompt},
                ]
            }
        ]
    }

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }

    timeout_s = float(os.getenv("GEMINI_TIMEOUT", "60"))
    with httpx.Client(timeout=timeout_s) as client:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    # typical: candidates[0].content.parts[0].text
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        raise RuntimeError(f"Unexpected Gemini response format: {e}; data={data!r}")


def set_description_status(engine: Engine, post_id: int, status: str, description: Optional[str] = None) -> None:
    with engine.begin() as conn:
        if description is None:
            conn.execute(
                text(
                    """
                    UPDATE post
                    SET description_status = :status
                    WHERE id = :post_id
                    """
                ),
                {"status": status, "post_id": post_id},
            )
        else:
            conn.execute(
                text(
                    """
                    UPDATE post
                    SET image_description = :desc,
                        description_status = :status
                    WHERE id = :post_id
                    """
                ),
                {"desc": description, "status": status, "post_id": post_id},
            )


def main() -> None:
    queue_name = os.getenv("RABBITMQ_DESCRIBE_QUEUE", "image_describe")
    image_root = Path(os.getenv("IMAGE_ROOT", "/app/uploads"))
    original_dir = image_root / "original"
    original_dir.mkdir(parents=True, exist_ok=True)

    prompt = os.getenv(
        "DESCRIBE_PROMPT",
        "Describe this image clearly and objectively for a visually impaired person. "
        "Focus on what is visible, including people, objects, actions, and setting. "
        "Do not speculate beyond what can be seen.",
    ) + " Limit the description to at most 3 sentences and under 300 characters."

    engine = make_engine()
    wait_for_db(engine)

    connection = wait_for_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_qos(prefetch_count=1)

    print(f"[describe-worker] Listening on queue: {queue_name}")

    def handle(ch, method, properties, body: bytes):
        post_id: Optional[int] = None
        filename: Optional[str] = None
        try:
            payload = json.loads(body.decode("utf-8"))
            post_id = int(payload["post_id"])
            filename = payload["filename"]

            img_path = original_dir / filename
            if not img_path.exists():
                set_description_status(engine, post_id, "FAILED")
                raise FileNotFoundError(f"Original image does not exist: {img_path}")

            # Mark pending (idempotent)
            set_description_status(engine, post_id, "PENDING")

            image_bytes = img_path.read_bytes()
            mime_type = mime_from_filename(filename)

            caption = gemini_caption(image_bytes, mime_type, prompt)

            set_description_status(engine, post_id, "READY", description=caption)
            print(f"[describe-worker] Post {post_id}: description READY")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"[describe-worker] Job failed: {e}")

            if post_id is not None:
                try:
                    set_description_status(engine, post_id, "FAILED")
                except Exception as db_err:
                    print(f"[describe-worker] Failed to update FAILED status: {db_err}")

            # Don't requeue by default (avoid infinite loops on bad jobs)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_consume(queue=queue_name, on_message_callback=handle)
    try:
        channel.start_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
