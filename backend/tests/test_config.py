"""Tests for configuration settings."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


from app.core.config import Settings


def test_正常系_デフォルト設定():
    """デフォルト設定が正しく設定されることを確認."""
    settings = Settings()

    assert settings.API_V1_STR == "/api/v1"
    assert settings.PROJECT_NAME == "Knowledge Management System"
    assert isinstance(settings.ALLOWED_HOSTS, list)
    assert "http://localhost:3000" in settings.ALLOWED_HOSTS
    assert settings.DEBUG is True
    assert settings.UPLOAD_DIRECTORY == "uploads"
    assert settings.MAX_UPLOAD_SIZE == 10 * 1024 * 1024


def test_正常系_CORS設定の検証():
    """CORS設定の検証が正常に動作することを確認."""
    # リスト形式
    settings = Settings(
        ALLOWED_HOSTS=["http://localhost:3000", "http://127.0.0.1:3000"]
    )
    assert len(settings.ALLOWED_HOSTS) == 2
    assert "http://localhost:3000" in settings.ALLOWED_HOSTS

    # 文字列形式（カンマ区切り）
    settings = Settings(ALLOWED_HOSTS="http://localhost:3000,http://127.0.0.1:3000")
    assert len(settings.ALLOWED_HOSTS) == 2
    assert "http://localhost:3000" in settings.ALLOWED_HOSTS


def test_正常系_データベースURL設定():
    """データベースURL設定が正常に動作することを確認."""
    # 直接指定
    custom_url = "postgresql://user:pass@localhost:5432/testdb"
    settings = Settings(DATABASE_URL=custom_url)
    assert custom_url == settings.DATABASE_URL


def test_正常系_環境変数からのデータベースURL構築():
    """環境変数からデータベースURLが正しく構築されることを確認."""
    # 環境変数を一時的に設定
    original_env = {}
    env_vars = {
        "DB_USER": "testuser",
        "DB_PASSWORD": "testpass",
        "DB_HOST": "testhost",
        "DB_PORT": "5433",
        "DB_NAME": "testdb",
    }

    # 環境変数を設定
    for key, value in env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    try:
        # DATABASE_URLを指定せずに環境変数から構築
        settings = Settings(DATABASE_URL=None)
        expected_url = "postgresql://testuser:testpass@testhost:5433/testdb"
        assert expected_url == settings.DATABASE_URL
    finally:
        # 環境変数を復元
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value
