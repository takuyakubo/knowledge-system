"""Dependency injection for FastAPI."""

from collections.abc import Generator
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import verify_token
from app.crud import user as crud_user
from app.models.user import User

# OAuth2スキーム（Bearer トークン）
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """Get database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials

    # JWTトークンを検証
    email = verify_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ユーザーを取得
    user = crud_user.user.get_by_email(db, email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # アクティブユーザーかチェック
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def get_current_verified_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Get current verified user."""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email not verified"
        )
    return current_user


def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough permissions"
        )
    return current_user


def get_current_user_optional(
    db: Annotated[Session, Depends(get_db)],
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_security),
) -> User | None:
    """Get current user (optional, for public endpoints)."""
    if credentials is None:
        return None

    token = credentials.credentials
    email = verify_token(token)
    if email is None:
        return None

    user = crud_user.user.get_by_email(db, email=email)
    if user is None or not user.is_active:
        return None

    return user


# 後方互換性のための仮実装（既存のAPIで使用）
def get_current_user_legacy() -> dict[str, Any]:
    """Placeholder for current user dependency (legacy).

    TODO: Remove this once all endpoints are updated to use proper authentication.
    """
    return {"id": 1, "email": "test@example.com", "is_active": True}
