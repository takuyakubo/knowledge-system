"""Application configuration."""

import os
import secrets

from pydantic import BaseModel, field_validator


class Settings(BaseModel):
    """Application settings."""

    # API設定
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Knowledge Management System"

    # CORS設定
    ALLOWED_HOSTS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3002",
    ]

    # データベース設定（開発環境ではSQLiteを使用）
    DATABASE_URL: str = "sqlite:///./knowledge_system.db"

    # 開発モード
    DEBUG: bool = True

    # ファイルアップロード設定
    UPLOAD_DIRECTORY: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # セキュリティ設定
    SECRET_KEY: str = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)

    # JWT設定
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # パスワードリセット設定
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24

    # セキュリティ設定
    PASSWORD_MIN_LENGTH: int = 8
    BCRYPT_ROUNDS: int = 12

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    AUTH_RATE_LIMIT_PER_MINUTE: int = 5

    # Session設定
    SESSION_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # メール設定（将来的に追加）
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_TLS: bool = True
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str | None = None

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        """CORS設定の検証."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None) -> str:
        """データベース接続URLの組み立て."""
        if isinstance(v, str):
            return v
        # 環境変数から構築
        return (
            f"postgresql://"
            f"{os.getenv('DB_USER', 'postgres')}:"
            f"{os.getenv('DB_PASSWORD', 'password')}@"
            f"{os.getenv('DB_HOST', 'localhost')}:"
            f"{os.getenv('DB_PORT', '5432')}/"
            f"{os.getenv('DB_NAME', 'knowledge_system')}"
        )

    model_config = {"case_sensitive": True, "env_file": ".env"}


settings = Settings()
