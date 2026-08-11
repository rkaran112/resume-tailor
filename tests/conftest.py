import os
from collections.abc import Generator

import psycopg
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401 -- register models on Base.metadata
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://resume_tailor:resume_tailor@localhost:5432/resume_tailor_test",
)


def _ensure_test_database_exists(url: str) -> None:
    """`docker compose up -d db` only creates the app's own database (via
    POSTGRES_DB), not this suite's separate `_test` database -- bootstrap it here
    so a fresh checkout doesn't need an undocumented manual `createdb` step.
    Connects to the server's built-in `postgres` admin database, which always
    exists regardless of POSTGRES_DB, to run `CREATE DATABASE` outside a
    transaction (autocommit)."""
    parsed = make_url(url)
    dbname = parsed.database
    admin_url = parsed.set(database="postgres").render_as_string(hide_password=False)
    admin_url = admin_url.replace("postgresql+psycopg://", "postgresql://")
    with psycopg.connect(admin_url, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
        if cur.fetchone() is None:
            cur.execute(f'CREATE DATABASE "{dbname}"')


_ensure_test_database_exists(TEST_DATABASE_URL)

engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def _create_schema() -> Generator[None, None, None]:
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def _default_feature_flags(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Pin feature flags to their shipped defaults so a developer's local .env
    (which typically enables them) can't change test behavior. Env vars take
    precedence over the .env file in pydantic-settings."""
    monkeypatch.setenv("ENABLE_RESUME_IMPORT", "false")
    monkeypatch.setenv("ENABLE_LLM_ENHANCE", "false")
    monkeypatch.setenv("ENABLE_COVER_LETTER", "false")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _clean_tables() -> Generator[None, None, None]:
    yield
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


def _override_get_db() -> Generator[Session, None, None]:
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    fastapi_app = create_app()
    fastapi_app.dependency_overrides[get_db] = _override_get_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
