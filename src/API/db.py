from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from .models import Base

# A scoped session is safe to reuse across requests inside Flask.
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False))


def init_db(app: Flask) -> None:

    database_url = app.config.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL must be set on the Flask app config")
    engine = create_engine(database_url, pool_pre_ping=True, future=True)
    SessionLocal.configure(bind=engine)
    Base.metadata.bind = engine

    @app.teardown_appcontext
    def cleanup_db(exception: Exception | None) -> None:  # pragma: no cover - Flask hook
        SessionLocal.remove()


@contextmanager
def get_session() -> Iterator[Session]: 

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
