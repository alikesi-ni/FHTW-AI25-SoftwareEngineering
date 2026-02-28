import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


class PostService:
    def __init__(self):
        self.conn = psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        self.conn.autocommit = True

    def add_post(self, image, comment, username):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO public.post (image, comment, username) VALUES (%s, %s, %s)",
                (image, comment, username)
            )

    def get_latest_post(self):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT image, comment, username FROM public.post ORDER BY id DESC LIMIT 1"
            )
            return cur.fetchone()
