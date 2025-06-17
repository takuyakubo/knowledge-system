"""Tests for article API endpoints."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app.deps import get_db
from app.main import app
from app.models.base import Base
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Setup test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_正常系_記事一覧取得(setup_database):
    """記事一覧を取得できることをテスト."""
    response = client.get("/api/v1/articles/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_正常系_記事作成(setup_database):
    """記事を作成できることをテスト."""
    article_data = {
        "title": "テスト記事",
        "content": "# テスト記事\n\nこれはテスト用の記事です。",
        "summary": "テスト記事の要約",
        "status": "draft",
        "is_public": False,
    }

    response = client.post("/api/v1/articles/", json=article_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "テスト記事"
    assert data["slug"] == "tesutoji-shi"
    assert data["status"] == "draft"
    assert data["is_public"] is False
    assert "id" in data
    assert "created_at" in data


def test_正常系_記事詳細取得(setup_database):
    """記事詳細を取得できることをテスト."""
    # まず記事を作成
    article_data = {
        "title": "詳細取得テスト記事",
        "content": "詳細取得のテスト用記事です。",
        "status": "published",
        "is_public": True,
    }

    create_response = client.post("/api/v1/articles/", json=article_data)
    assert create_response.status_code == 200
    created_article = create_response.json()
    article_id = created_article["id"]

    # 記事詳細を取得
    response = client.get(f"/api/v1/articles/{article_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == article_id
    assert data["title"] == "詳細取得テスト記事"


def test_正常系_記事更新(setup_database):
    """記事を更新できることをテスト."""
    # まず記事を作成
    article_data = {"title": "更新前記事", "content": "更新前の内容", "status": "draft"}

    create_response = client.post("/api/v1/articles/", json=article_data)
    created_article = create_response.json()
    article_id = created_article["id"]

    # 記事を更新
    update_data = {
        "title": "更新後記事",
        "content": "更新後の内容",
        "status": "published",
    }

    response = client.put(f"/api/v1/articles/{article_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "更新後記事"
    assert data["content"] == "更新後の内容"
    assert data["status"] == "published"


def test_正常系_記事公開(setup_database):
    """記事を公開できることをテスト."""
    # まず下書き記事を作成
    article_data = {
        "title": "公開テスト記事",
        "content": "公開テスト用の記事です。",
        "status": "draft",
        "is_public": False,
    }

    create_response = client.post("/api/v1/articles/", json=article_data)
    created_article = create_response.json()
    article_id = created_article["id"]

    # 記事を公開
    response = client.post(f"/api/v1/articles/{article_id}/publish")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"
    assert data["is_public"] is True
    assert data["published_at"] is not None


def test_正常系_スラッグで記事取得(setup_database):
    """スラッグで記事を取得できることをテスト."""
    # カスタムスラッグで記事を作成
    article_data = {
        "title": "カスタムスラッグ記事",
        "content": "カスタムスラッグのテスト",
        "slug": "custom-slug-article",
        "status": "published",
        "is_public": True,
    }

    create_response = client.post("/api/v1/articles/", json=article_data)
    assert create_response.status_code == 200

    # スラッグで取得
    response = client.get("/api/v1/articles/slug/custom-slug-article")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "custom-slug-article"
    assert data["title"] == "カスタムスラッグ記事"


def test_異常系_存在しない記事取得(setup_database):
    """存在しない記事を取得しようとした場合のエラーハンドリングをテスト."""
    response = client.get("/api/v1/articles/99999")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Article not found"


def test_正常系_記事削除(setup_database):
    """記事を削除できることをテスト."""
    # まず記事を作成
    article_data = {"title": "削除テスト記事", "content": "削除テスト用の記事です。"}

    create_response = client.post("/api/v1/articles/", json=article_data)
    created_article = create_response.json()
    article_id = created_article["id"]

    # 記事を削除
    response = client.delete(f"/api/v1/articles/{article_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Article deleted successfully"

    # 削除された記事は取得できない
    get_response = client.get(f"/api/v1/articles/{article_id}")
    assert get_response.status_code == 404
