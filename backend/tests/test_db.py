"""Tests for database session configuration."""

import pytest
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.session import SessionLocal, engine, get_db


def test_engine_uses_settings_url() -> None:
    engine_url = engine.url
    settings_url = make_url(get_settings().database_url)

    assert engine_url.drivername == settings_url.drivername
    assert engine_url.host == settings_url.host
    assert engine_url.port == settings_url.port
    assert engine_url.database == settings_url.database
    assert engine_url.username == settings_url.username
    assert engine_url.password == settings_url.password
    assert dict(engine_url.query) == dict(settings_url.query)


def test_engine_uses_psycopg_driver() -> None:
    assert engine.dialect.name == "postgresql"
    assert engine.dialect.driver == "psycopg"


def test_session_local_is_sessionmaker() -> None:
    assert isinstance(SessionLocal, sessionmaker)


def test_get_db_yields_a_session() -> None:
    generator = get_db()
    session = next(generator)

    try:
        assert isinstance(session, Session)
    finally:
        generator.close()


def test_get_db_closes_session_after_exhaustion(monkeypatch) -> None:
    generator = get_db()
    session = next(generator)

    closed = []
    monkeypatch.setattr(session, "close", lambda: closed.append(True))

    with pytest.raises(StopIteration):
        next(generator)

    assert closed, "Session.close() was not called"