"""Pytest configuration for backend API tests."""

import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from app.core.database import Base
from app.deps import get_db
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def test_db() -> Iterator[sessionmaker]:
    """Create a test database."""
    # Create a temporary file for the test database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()

    # Create engine and session
    test_engine = create_engine(
        f"sqlite:///{temp_db.name}",
        connect_args={"check_same_thread": False},
    )

    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    yield TestingSessionLocal

    # Cleanup
    Path(temp_db.name).unlink()


@pytest.fixture
def db_session(test_db: sessionmaker):
    """Create a database session for testing."""
    session = test_db()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(test_db: sessionmaker) -> TestClient:
    """Create a test client with test database."""

    def override_get_db():
        try:
            db = test_db()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
