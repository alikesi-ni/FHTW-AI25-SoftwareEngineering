import json
import os
import pika


def _amqp_params() -> pika.ConnectionParameters:
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")
    return pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=pika.PlainCredentials(user, password),
    )

def publish_resize_job(filename: str) -> None:
    queue_name = os.getenv("RABBITMQ_QUEUE", "image_resize")

    connection = pika.BlockingConnection(_amqp_params())
    try:
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)

        body = json.dumps({"filename": filename}).encode("utf-8")
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2  # make message persistent
            ),
        )
    finally:
        connection.close()


def publish_sentiment_job(post_id: int) -> None:
    queue_name = os.getenv("RABBITMQ_SENTIMENT_QUEUE", "sentiment_analyze")

    connection = pika.BlockingConnection(_amqp_params())
    try:
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)

        body = json.dumps({"post_id": post_id}).encode("utf-8")
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ),
        )
    finally:
        connection.close()


def publish_describe_job(post_id: int) -> None:
    queue_name = os.getenv("RABBITMQ_DESCRIBE_QUEUE", "describe_requests")
    payload = {"post_id": post_id}

    conn = pika.BlockingConnection(_amqp_params())
    ch = conn.channel()
    ch.queue_declare(queue=queue_name, durable=True)

    ch.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=json.dumps(payload).encode("utf-8"),
        properties=pika.BasicProperties(delivery_mode=2),  # persistent
    )

    conn.close()
    
