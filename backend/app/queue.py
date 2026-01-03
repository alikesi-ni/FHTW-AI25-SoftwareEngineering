import json
import os
import pika


def _amqp_params() -> pika.ConnectionParameters:
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")

    credentials = pika.PlainCredentials(user, password)
    return pika.ConnectionParameters(host=host, port=port, credentials=credentials)


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

