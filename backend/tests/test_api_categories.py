"""Tests for Category API endpoints."""

from fastapi.testclient import TestClient


def test_正常系_カテゴリ一覧取得(client: TestClient):
    """カテゴリ一覧が正常に取得できることを確認."""
    response = client.get("/api/v1/categories/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_正常系_カテゴリ作成(client: TestClient):
    """新しいカテゴリが正常に作成できることを確認."""
    category_data = {
        "name": "Technology",
        "description": "Technology related content",
        "color": "#3498db",
        "icon": "tech",
    }
    response = client.post("/api/v1/categories/", json=category_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == category_data["name"]
    assert data["description"] == category_data["description"]
    assert data["color"] == category_data["color"]
    assert data["icon"] == category_data["icon"]
    assert "slug" in data
    assert data["level"] == 0  # ルートカテゴリ
    assert data["path"].startswith("/")
    assert data["is_active"] is True
    assert data["article_count"] == 0
    assert data["paper_count"] == 0
    return data["id"]  # 他のテストで使用


def test_正常系_カテゴリ詳細取得(client: TestClient):
    """カテゴリ詳細が正常に取得できることを確認."""
    # まずカテゴリを作成
    category_data = {"name": "Science", "description": "Science content"}
    create_response = client.post("/api/v1/categories/", json=category_data)
    category_id = create_response.json()["id"]

    # 詳細を取得
    response = client.get(f"/api/v1/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == category_data["name"]


def test_正常系_スラッグでカテゴリ取得(client: TestClient):
    """スラッグでカテゴリが正常に取得できることを確認."""
    # カテゴリを作成
    category_data = {"name": "Machine Learning", "slug": "ml"}
    create_response = client.post("/api/v1/categories/", json=category_data)
    created_data = create_response.json()

    # スラッグで取得
    response = client.get(f"/api/v1/categories/slug/{created_data['slug']}")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == created_data["slug"]
    assert data["name"] == category_data["name"]


def test_正常系_子カテゴリ作成(client: TestClient):
    """子カテゴリが正常に作成できることを確認."""
    # 親カテゴリを作成
    parent_data = {"name": "Programming"}
    parent_response = client.post("/api/v1/categories/", json=parent_data)
    parent_id = parent_response.json()["id"]

    # 子カテゴリを作成
    child_data = {
        "name": "Python",
        "parent_id": parent_id,
        "description": "Python programming",
    }
    response = client.post("/api/v1/categories/", json=child_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == child_data["name"]
    assert data["parent_id"] == parent_id
    assert data["level"] == 1  # 子カテゴリなのでレベル1
    assert "/python" in data["path"]  # パスに含まれる


def test_正常系_カテゴリ更新(client: TestClient):
    """カテゴリが正常に更新できることを確認."""
    # カテゴリを作成
    category_data = {"name": "Original Name"}
    create_response = client.post("/api/v1/categories/", json=category_data)
    category_id = create_response.json()["id"]

    # 更新
    update_data = {
        "name": "Updated Name",
        "description": "Updated description",
        "color": "#e74c3c",
    }
    response = client.put(f"/api/v1/categories/{category_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["color"] == update_data["color"]


def test_正常系_カテゴリツリー取得(client: TestClient):
    """階層構造のカテゴリツリーが正常に取得できることを確認."""
    response = client.get("/api/v1/categories/tree")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # ツリー構造の場合、各要素には children フィールドがある
    if data:
        assert "children" in data[0]


def test_正常系_ルートカテゴリ取得(client: TestClient):
    """ルートカテゴリが正常に取得できることを確認."""
    response = client.get("/api/v1/categories/roots")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # 全てレベル0のはず
    for category in data:
        assert category["level"] == 0
        assert category["parent_id"] is None


def test_正常系_子カテゴリ取得(client: TestClient):
    """指定カテゴリの子カテゴリが正常に取得できることを確認."""
    # 親カテゴリを作成
    parent_data = {"name": "Web Development"}
    parent_response = client.post("/api/v1/categories/", json=parent_data)
    parent_id = parent_response.json()["id"]

    # 子カテゴリを作成
    child_data = {"name": "Frontend", "parent_id": parent_id}
    client.post("/api/v1/categories/", json=child_data)

    # 子カテゴリを取得
    response = client.get(f"/api/v1/categories/{parent_id}/children")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert data[0]["parent_id"] == parent_id
        assert data[0]["level"] == 1


def test_正常系_カテゴリ移動(client: TestClient):
    """カテゴリの移動が正常に実行できることを確認."""
    # 2つの親カテゴリを作成
    parent1_data = {"name": "Parent 1"}
    parent1_response = client.post("/api/v1/categories/", json=parent1_data)
    parent1_id = parent1_response.json()["id"]

    parent2_data = {"name": "Parent 2"}
    parent2_response = client.post("/api/v1/categories/", json=parent2_data)
    parent2_id = parent2_response.json()["id"]

    # 子カテゴリを作成（最初はparent1の下）
    child_data = {"name": "Child", "parent_id": parent1_id}
    child_response = client.post("/api/v1/categories/", json=child_data)
    child_id = child_response.json()["id"]

    # parent2の下に移動
    move_data = {"new_parent_id": parent2_id}
    response = client.post(f"/api/v1/categories/{child_id}/move", json=move_data)
    assert response.status_code == 200
    data = response.json()
    assert data["parent_id"] == parent2_id


def test_正常系_カテゴリ検索(client: TestClient):
    """カテゴリ検索が正常に実行できることを確認."""
    # 検索用カテゴリを作成
    category_data = {"name": "Data Science", "description": "Data analysis and science"}
    client.post("/api/v1/categories/", json=category_data)

    # 検索実行
    response = client.get("/api/v1/categories/search?q=Data")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "has_next" in data


def test_正常系_人気カテゴリ取得(client: TestClient):
    """人気カテゴリが正常に取得できることを確認."""
    response = client.get("/api/v1/categories/popular")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_正常系_統計情報取得(client: TestClient):
    """カテゴリ統計情報が正常に取得できることを確認."""
    response = client.get("/api/v1/categories/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_categories" in data
    assert "active_categories" in data
    assert "root_categories" in data
    assert "max_depth" in data
    assert "categories_by_level" in data
    assert "top_categories" in data


def test_正常系_カテゴリ有効化(client: TestClient):
    """カテゴリの有効化が正常に実行できることを確認."""
    # カテゴリを作成
    category_data = {"name": "Test Category"}
    create_response = client.post("/api/v1/categories/", json=category_data)
    category_id = create_response.json()["id"]

    # 有効化（すでに有効だが動作確認）
    response = client.post(f"/api/v1/categories/{category_id}/activate")
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is True


def test_正常系_カテゴリ無効化(client: TestClient):
    """カテゴリの無効化が正常に実行できることを確認."""
    # カテゴリを作成
    category_data = {"name": "Test Category 2"}
    create_response = client.post("/api/v1/categories/", json=category_data)
    category_id = create_response.json()["id"]

    # 無効化
    response = client.post(f"/api/v1/categories/{category_id}/deactivate")
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False


def test_正常系_フィルター付きカテゴリ取得(client: TestClient):
    """フィルター条件付きでカテゴリが正常に取得できることを確認."""
    # テスト用カテゴリを作成
    category_data = {"name": "Filter Test", "color": "#ff5733"}
    client.post("/api/v1/categories/", json=category_data)

    # 色でフィルター
    response = client.get("/api/v1/categories/?color=%23ff5733")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # レベルでフィルター
    response = client.get("/api/v1/categories/?level=0")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for category in data:
        assert category["level"] == 0


def test_異常系_存在しないカテゴリ取得(client: TestClient):
    """存在しないカテゴリの取得で404エラーが返されることを確認."""
    response = client.get("/api/v1/categories/99999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_異常系_存在しないスラッグ(client: TestClient):
    """存在しないスラッグで404エラーが返されることを確認."""
    response = client.get("/api/v1/categories/slug/nonexistent")
    assert response.status_code == 404


def test_異常系_無効な色指定(client: TestClient):
    """無効な色指定で400エラーが返されることを確認."""
    category_data = {
        "name": "Invalid Color",
        "color": "invalid-color",  # 無効なHEXカラー
    }
    response = client.post("/api/v1/categories/", json=category_data)
    assert response.status_code == 422  # バリデーションエラー


def test_異常系_存在しない親カテゴリ指定(client: TestClient):
    """存在しない親カテゴリを指定した場合に400エラーが返されることを確認."""
    category_data = {
        "name": "Invalid Parent",
        "parent_id": 99999,  # 存在しない親ID
    }
    response = client.post("/api/v1/categories/", json=category_data)
    assert response.status_code == 400
    data = response.json()
    assert "not found" in data["detail"]


def test_エッジケース_空の検索クエリ(client: TestClient):
    """空の検索クエリで400エラーが返されることを確認."""
    response = client.get("/api/v1/categories/search?q=")
    assert response.status_code == 422  # バリデーションエラー（min_length=1）
