"""Pytest configuration and fixtures."""

import os
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from knowledge_system.core.example import ExampleClass, ExampleConfig

# Backend API testing imports
try:
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from backend.app.core.database import Base
    from backend.app.deps import get_db
    from backend.app.main import app

    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False


@pytest.fixture
def example_config() -> ExampleConfig:
    """Create a test configuration."""
    return ExampleConfig(
        name="test",
        max_items=10,
        enable_validation=True,
    )


@pytest.fixture
def example_instance(example_config: ExampleConfig) -> ExampleClass:
    """Create a test ExampleClass instance."""
    return ExampleClass(example_config)


@pytest.fixture
def sample_data() -> list[dict[str, Any]]:
    """Create sample data for testing."""
    return [
        {"id": 1, "name": "Item 1", "value": 100},
        {"id": 2, "name": "Item 2", "value": 200},
        {"id": 3, "name": "Item 3", "value": 300},
    ]


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset environment variables for each test."""
    # Remove any test-specific environment variables
    test_env_vars = [var for var in os.environ if var.startswith("TEST_")]
    for var in test_env_vars:
        monkeypatch.delenv(var, raising=False)


# Backend API testing fixtures
if BACKEND_AVAILABLE:

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
