import json
import os
import time
from pathlib import Path

import pika
from PIL import Image


def amqp_params() -> pika.ConnectionParameters:
    host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")
    credentials = pika.PlainCredentials(user, password)
    return pika.ConnectionParameters(host=host, port=port, credentials=credentials)


def ensure_dirs(image_root: Path) -> tuple[Path, Path]:
    original_dir = image_root / "original"
    reduced_dir = image_root / "reduced"
    original_dir.mkdir(parents=True, exist_ok=True)
    reduced_dir.mkdir(parents=True, exist_ok=True)
    return original_dir, reduced_dir


def resize_image(src: Path, dst: Path, max_width: int = 512) -> None:
    # Keep aspect ratio, constrain by width (and height implicitly)
    with Image.open(src) as im:
        im = im.convert("RGB") if im.mode in ("P", "RGBA") else im
        w, h = im.size
        if w <= max_width:
            # already small enough; still write to reduced to satisfy “exists”
            dst.parent.mkdir(parents=True, exist_ok=True)
            im.save(dst, quality=85, optimize=True)
            return

        new_h = int(h * (max_width / w))
        im = im.resize((max_width, new_h))
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst, quality=85, optimize=True)


def main() -> None:
    queue_name = os.getenv("RABBITMQ_QUEUE", "image_resize")
    image_root = Path(os.getenv("IMAGE_ROOT", "/app/uploads"))
    original_dir, reduced_dir = ensure_dirs(image_root)

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
    channel.basic_qos(prefetch_count=1)

    print(f"[worker] Listening on queue: {queue_name}")

    def handle(ch, method, properties, body: bytes):
        try:
            payload = json.loads(body.decode("utf-8"))
            filename = payload["filename"]
            src = original_dir / filename
            dst = reduced_dir / filename

            if not src.exists():
                raise FileNotFoundError(f"Original image does not exist: {src}")

            # Idempotency: if already resized, just ack
            if dst.exists():
                print(f"[worker] Reduced already exists, skipping: {dst}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            resize_image(src, dst, max_width=int(payload.get("max_width", 512)))
            print(f"[worker] Wrote reduced image: {dst}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            # If you want retries, nack with requeue=True.
            # For an exercise, requeue can cause infinite loops on a bad image.
            print(f"[worker] Job failed: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_consume(queue=queue_name, on_message_callback=handle)
    try:
        channel.start_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
