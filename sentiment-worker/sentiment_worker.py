import json
import os
import time

import pika
from transformers import pipeline
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

SENTIMENT_QUEUE_NAME = os.getenv("RABBITMQ_SENTIMENT_QUEUE", "sentiment_analyze")


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
            print("[sentiment-worker] DB is ready")
            return
        except Exception as exc:
            print(f"[sentiment-worker] DB not ready yet: {exc}")
            time.sleep(2)


def load_post_content(engine: Engine, post_id: int) -> str | None:
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT content FROM post WHERE id = :post_id"),
            {"post_id": post_id},
        ).mappings().first()

    if row is None:
        return None

    content = (row["content"] or "").strip()
    return content or None


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


def main() -> None:
    engine = make_engine()
    wait_for_db(engine)

    nlp = pipeline(
        "sentiment-analysis",
        model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    )
    print("[sentiment-worker] Model loaded")

    while True:
        try:
            connection = pika.BlockingConnection(amqp_params())
            break
        except Exception as exc:
            print(f"[sentiment-worker] RabbitMQ not ready: {exc}")
            time.sleep(2)

    channel = connection.channel()
    channel.queue_declare(queue=SENTIMENT_QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    print(f"[sentiment-worker] Listening on queue: {SENTIMENT_QUEUE_NAME}")

    def handle(ch, method, properties, body: bytes) -> None:
        try:
            payload = json.loads(body.decode("utf-8"))
            post_id = int(payload["post_id"])
        except Exception as exc:
            print(f"[sentiment-worker] Bad message: {exc} / {body!r}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        try:
            content = load_post_content(engine, post_id)
            if not content:
                print(f"[sentiment-worker] Post {post_id} has no content")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            result = nlp(content[:512])[0]
            raw_label = result["label"].upper()
            score = float(result["score"])
            label = "POSITIVE" if "POSITIVE" in raw_label else "NEGATIVE"

            update_sentiment(engine, post_id, label, score)
            print(
                f"[sentiment-worker] Sentiment updated for post {post_id}: "
                f"{label} ({score:.3f})"
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as exc:
            print(f"[sentiment-worker] Error processing post {post_id}: {exc}")
            # do not requeue for now
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=SENTIMENT_QUEUE_NAME, on_message_callback=handle)

    try:
        channel.start_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
