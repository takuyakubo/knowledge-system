"""Application configuration."""

import os

from pydantic import BaseModel, field_validator


class Settings(BaseModel):
    """Application settings."""

    # API設定
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Knowledge Management System"

    # CORS設定
    ALLOWED_HOSTS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # データベース設定
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/knowledge_system"

    # 開発モード
    DEBUG: bool = True

    # ファイルアップロード設定
    UPLOAD_DIRECTORY: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

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
