"""Shared pytest fixtures and plugin registration."""

pytest_plugins = ["tests.fixtures"]

from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.deps import get_embedding_provider, get_llm_provider, get_storage
from app.main import create_app
from app.services.storage import LocalDiskStorage
from tests.doubles import FakeEmbeddingProvider, FakeLLMProvider


@pytest.fixture()
def app() -> FastAPI:
    """A fresh application instance."""
    return create_app()


@pytest.fixture()
def client(app: FastAPI):
    """A TestClient with application lifespan (startup/shutdown) run."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def test_engine():
    """Engine bound to the dedicated test database (skips if unreachable)."""
    url = get_settings().test_database_url
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            connection.commit()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"Test database unreachable at {url}: {exc}")
    yield engine
    engine.dispose()


@pytest.fixture()
def test_sessionmaker(test_engine) -> sessionmaker:
    return sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def db_session(test_sessionmaker: sessionmaker) -> Generator[Session, None, None]:
    """A clean, function-scoped session bound to the test database."""
    session = test_sessionmaker()
    session.execute(text("DELETE FROM chunks"))
    session.execute(text("DELETE FROM documents"))
    session.commit()
    yield session
    session.close()


@pytest.fixture()
def db_client(tmp_path, db_session: Session):
    """TestClient with DB session + storage overridden for the test database."""
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    storage = LocalDiskStorage(tmp_path / "uploads")
    app.dependency_overrides[get_storage] = lambda: storage

    embeddings = FakeEmbeddingProvider()
    app.dependency_overrides[get_embedding_provider] = lambda: embeddings

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def chat_client(tmp_path, db_session: Session):
    """TestClient with DB, storage, embeddings, and LLM all overridden."""
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_storage] = lambda: LocalDiskStorage(
        tmp_path / "uploads"
    )
    app.dependency_overrides[get_embedding_provider] = lambda: FakeEmbeddingProvider()

    fake_llm = FakeLLMProvider()
    app.dependency_overrides[get_llm_provider] = lambda: fake_llm

    with TestClient(app) as test_client:
        yield test_client, fake_llm