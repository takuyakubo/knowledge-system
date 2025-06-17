"""Dependency injection for FastAPI."""

from collections.abc import Generator
from typing import Any

from sqlalchemy.orm import Session

from app.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Get database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user() -> dict[str, Any]:
    """Placeholder for current user dependency.

    TODO: Implement proper authentication once User model and auth system are ready.
    """
    return {"id": 1, "email": "test@example.com", "is_active": True}
