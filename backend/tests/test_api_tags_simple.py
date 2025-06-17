"""Simple tests for Tag API endpoints."""

from fastapi.testclient import TestClient


def test_正常系_タグ一覧取得(client: TestClient):
    """タグ一覧が正常に取得できることを確認."""
    response = client.get("/api/v1/tags/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_正常系_タグ作成(client: TestClient):
    """新しいタグが正常に作成できることを確認."""
    tag_data = {
        "name": "Python",
        "description": "Python programming language",
    }
    response = client.post("/api/v1/tags/", json=tag_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == tag_data["name"]
    assert data["description"] == tag_data["description"]
    assert "slug" in data
    assert data["usage_count"] == 0
    assert data["is_active"] is True


def test_正常系_タグ詳細取得(client: TestClient):
    """タグ詳細が正常に取得できることを確認."""
    # まずタグを作成
    tag_data = {"name": "JavaScript"}
    create_response = client.post("/api/v1/tags/", json=tag_data)
    tag_id = create_response.json()["id"]

    # 詳細を取得
    response = client.get(f"/api/v1/tags/{tag_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tag_id
    assert data["name"] == tag_data["name"]


def test_異常系_存在しないタグ取得(client: TestClient):
    """存在しないタグの取得で404エラーが返されることを確認."""
    response = client.get("/api/v1/tags/99999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]
