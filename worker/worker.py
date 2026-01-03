import json
import os
import time
from pathlib import Path

import pika
from PIL import Image

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from transformers import pipeline

# load once, reuse for all messages
sentiment_analyzer = pipeline("sentiment-analysis")

SENTIMENT_QUEUE_NAME = os.getenv("RABBITMQ_SENTIMENT_QUEUE", "sentiment_analyze")

def amqp_params() -> pika.ConnectionParameters:
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")
    credentials = pika.PlainCredentials(user, password)
    return pika.ConnectionParameters(host=host, port=port, credentials=credentials)


def db_url() -> str:
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "social")
    user = os.getenv("DB_USER", "admin")
    pw = os.getenv("DB_PASSWORD", "password")
    return f"postgresql+psycopg://{user}:{pw}@{host}:{port}/{name}"


def make_engine() -> Engine:
    # pool_pre_ping avoids stale connections
    return create_engine(db_url(), pool_pre_ping=True)


def ensure_dirs(image_root: Path) -> tuple[Path, Path]:
    original_dir = image_root / "original"
    reduced_dir = image_root / "reduced"
    original_dir.mkdir(parents=True, exist_ok=True)
    reduced_dir.mkdir(parents=True, exist_ok=True)
    return original_dir, reduced_dir


def resize_image(src: Path, dst: Path, max_width: int = 512) -> None:
    with Image.open(src) as im:
        # Ensure we have an alpha channel if the source is paletted/translucent
        if im.mode in ("P", "RGBA", "LA"):
            im = im.convert("RGBA")

            # Flatten transparency onto white
            white_bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
            im = Image.alpha_composite(white_bg, im).convert("RGB")
        else:
            # No transparency; normalize to RGB for consistent saving
            im = im.convert("RGB")

        w, h = im.size
        if w > max_width:
            new_h = int(h * (max_width / w))
            im = im.resize((max_width, new_h), Image.LANCZOS)

        dst.parent.mkdir(parents=True, exist_ok=True)

        # Save in the same extension as dst (png stays png, jpg stays jpg)
        ext = dst.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            im.save(dst, quality=85, optimize=True)
        else:
            # PNG (or anything else) as PNG
            im.save(dst, format="PNG", optimize=True)



def wait_for_db(engine: Engine) -> None:
    while True:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception as e:
            print(f"[worker] DB not ready yet: {e}. Retrying...")
            time.sleep(2)


def update_status(engine: Engine, filename: str, status: str) -> None:
    """
    Update image_status for the post with the given image_filename.
    Safe to call multiple times (idempotent).
    """
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE post
                SET image_status = :status
                WHERE image_filename = :filename
                """
            ),
            {"status": status, "filename": filename},
        )


def main() -> None:
    queue_name = os.getenv("RABBITMQ_QUEUE", "image_resize")
    sentiment_queue_name = SENTIMENT_QUEUE_NAME
    image_root = Path(os.getenv("IMAGE_ROOT", "/app/uploads"))
    original_dir, reduced_dir = ensure_dirs(image_root)

    engine = make_engine()
    wait_for_db(engine)

    # Wait/retry loop for RabbitMQ readiness
    while True:
        try:
            connection = pika.BlockingConnection(amqp_params())
            break
        except Exception as e:
            print(f"[worker] RabbitMQ not ready yet: {e}. Retrying...")
            time.sleep(2)

    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_declare(queue=sentiment_queue_name, durable=True)
    channel.basic_qos(prefetch_count=1)

    print(f"[worker] Listening on queue: {queue_name}")
    print(f"[worker] Listening on sentiment queue: {sentiment_queue_name}")


    def handle(ch, method, properties, body: bytes):
        filename = None
        try:
            payload = json.loads(body.decode("utf-8"))
            filename = payload["filename"]
            src = original_dir / filename
            dst = reduced_dir / filename

            if not src.exists():
                # mark failed because original is missing
                update_status(engine, filename, "FAILED")
                raise FileNotFoundError(f"Original image does not exist: {src}")

            # Idempotency: if already resized, ensure READY and ack
            if dst.exists():
                update_status(engine, filename, "READY")
                print(f"[worker] Reduced already exists, marked READY: {dst}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            resize_image(src, dst, max_width=int(payload.get("max_width", 512)))
            update_status(engine, filename, "READY")
            print(f"[worker] Wrote reduced image, marked READY: {dst}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            # Mark FAILED if we know which post it was
            if filename:
                try:
                    update_status(engine, filename, "FAILED")
                except Exception as db_err:
                    print(f"[worker] Failed to update status to FAILED: {db_err}")

            # For the exercise, don't requeue forever on bad input
            print(f"[worker] Job failed: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    
    def update_sentiment(engine: Engine, post_id: int, label: str, score: float) -> None:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE post "
                    "SET sentiment_status = :status, "
                    "sentiment_label = :label, "
                    "sentiment_score = :score "
                    "WHERE id = :post_id"
                ),
                {
                    "status": "READY",
                    "label": label,
                    "score": score,
                    "post_id": post_id,
                },
            )

    def process_sentiment_message(ch, method, properties, body) -> None:
        try:
            payload = json.loads(body.decode("utf-8"))
            post_id = int(payload["post_id"])
        except (ValueError, KeyError, json.JSONDecodeError):
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        try:
            # 1) Read post content from DB
            with engine.connect() as conn:
                row = conn.execute(
                    text("SELECT content FROM post WHERE id = :post_id"),
                    {"post_id": post_id},
                ).first()

            if not row or not row[0]:
                print(f"[worker] No content for post {post_id}, skipping sentiment.")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            content = row[0]

            # 2) Run ML model
            result = sentiment_analyzer(str(content))[0]
            raw_label = result.get("label", "")
            score = float(result.get("score", 0.0))

            if raw_label in ("POSITIVE", "NEGATIVE"):
                label = raw_label
            elif "1" in raw_label:
                label = "POSITIVE"
            else:
                label = "NEGATIVE"

            # 3) Store result in DB
            update_sentiment(engine, post_id, label, score)
            print(f"[worker] Sentiment updated for post {post_id}: {label} ({score:.3f})")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"[worker] Sentiment job failed for post {post_id}: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.basic_consume(queue=queue_name, on_message_callback=handle)
    channel.basic_consume(
        queue=sentiment_queue_name,
        on_message_callback=process_sentiment_message,
    )
    try:
        channel.start_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
