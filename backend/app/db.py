import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


def _db_url() -> str:
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "social")
    user = os.getenv("DB_USER", "admin")
    pw = os.getenv("DB_PASSWORD", "password")
    return f"postgresql+psycopg://{user}:{pw}@{host}:{port}/{name}"


engine = create_engine(_db_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass
