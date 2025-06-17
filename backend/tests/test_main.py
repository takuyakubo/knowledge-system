"""Tests for main FastAPI application."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_正常系_ルートエンドポイント():
    """ルートエンドポイントが正常に応答することを確認."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Welcome to Knowledge Management System API" in data["message"]
    assert data["docs"] == "/docs"
    assert data["redoc"] == "/redoc"


def test_正常系_ヘルスチェックエンドポイント():
    """ヘルスチェックエンドポイントが正常に応答することを確認."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Knowledge Management System API is running" in data["message"]


def test_正常系_OpenAPI仕様書の取得():
    """OpenAPI仕様書が正常に取得できることを確認."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "Knowledge Management System API"
    assert data["info"]["version"] == "0.1.0"


def test_正常系_API文書の表示():
    """Swagger UI が正常に表示されることを確認."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_正常系_ReDoc文書の表示():
    """ReDoc が正常に表示されることを確認."""
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
