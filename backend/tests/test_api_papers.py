"""Tests for Paper API endpoints."""

from fastapi.testclient import TestClient


def test_正常系_論文一覧取得(client: TestClient):
    """論文一覧が正常に取得できることを確認."""
    response = client.get("/api/v1/papers/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_正常系_論文作成(client: TestClient):
    """新しい論文が正常に作成できることを確認."""
    paper_data = {
        "title": "Deep Learning for Natural Language Processing",
        "authors": "John Doe, Jane Smith",
        "abstract": "This paper presents a novel approach to NLP using deep learning.",
        "publication_year": 2023,
        "paper_type": "journal",
        "language": "en",
        "reading_status": "to_read",
        "priority": 4,
        "is_favorite": False,
        "tag_ids": [],
    }
    response = client.post("/api/v1/papers/", json=paper_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == paper_data["title"]
    assert data["authors"] == paper_data["authors"]
    assert data["publication_year"] == paper_data["publication_year"]
    assert data["reading_status"] == "to_read"
    assert data["priority"] == 4
    assert data["is_favorite"] is False


def test_正常系_論文詳細取得(client: TestClient):
    """論文詳細が正常に取得できることを確認."""
    # まず論文を作成
    paper_data = {
        "title": "Machine Learning Fundamentals",
        "authors": "Alice Johnson",
        "publication_year": 2022,
        "tag_ids": [],
    }
    create_response = client.post("/api/v1/papers/", json=paper_data)
    paper_id = create_response.json()["id"]

    # 詳細を取得
    response = client.get(f"/api/v1/papers/{paper_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == paper_id
    assert data["title"] == paper_data["title"]


def test_正常系_論文更新(client: TestClient):
    """論文が正常に更新できることを確認."""
    # まず論文を作成
    paper_data = {
        "title": "Original Title",
        "authors": "Original Author",
        "tag_ids": [],
    }
    create_response = client.post("/api/v1/papers/", json=paper_data)
    paper_id = create_response.json()["id"]

    # 更新
    update_data = {
        "title": "Updated Title",
        "abstract": "Updated abstract content",
        "priority": 5,
    }
    response = client.put(f"/api/v1/papers/{paper_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["abstract"] == "Updated abstract content"
    assert data["priority"] == 5


def test_正常系_論文評価(client: TestClient):
    """論文の評価が正常に設定できることを確認."""
    # まず論文を作成
    paper_data = {
        "title": "Paper to Rate",
        "authors": "Test Author",
        "tag_ids": [],
    }
    create_response = client.post("/api/v1/papers/", json=paper_data)
    paper_id = create_response.json()["id"]

    # 評価を設定
    rating_data = {"rating": 4}
    response = client.post(f"/api/v1/papers/{paper_id}/rating", json=rating_data)
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 4


def test_正常系_読書ステータス更新(client: TestClient):
    """読書ステータスが正常に更新できることを確認."""
    # まず論文を作成
    paper_data = {
        "title": "Paper to Read",
        "authors": "Test Author",
        "tag_ids": [],
    }
    create_response = client.post("/api/v1/papers/", json=paper_data)
    paper_id = create_response.json()["id"]

    # ステータスを更新
    status_data = {"reading_status": "completed"}
    response = client.post(f"/api/v1/papers/{paper_id}/status", json=status_data)
    assert response.status_code == 200
    data = response.json()
    assert data["reading_status"] == "completed"
    assert data["read_at"] is not None


def test_正常系_お気に入り切り替え(client: TestClient):
    """お気に入り状態が正常に切り替えられることを確認."""
    # まず論文を作成
    paper_data = {
        "title": "Paper to Favorite",
        "authors": "Test Author",
        "is_favorite": False,
        "tag_ids": [],
    }
    create_response = client.post("/api/v1/papers/", json=paper_data)
    paper_id = create_response.json()["id"]

    # お気に入りに設定
    response = client.post(f"/api/v1/papers/{paper_id}/favorite")
    assert response.status_code == 200
    data = response.json()
    assert data["is_favorite"] is True

    # お気に入りを解除
    response = client.post(f"/api/v1/papers/{paper_id}/favorite")
    assert response.status_code == 200
    data = response.json()
    assert data["is_favorite"] is False


def test_正常系_DOIで論文取得(client: TestClient):
    """DOIで論文が正常に取得できることを確認."""
    # DOI付きの論文を作成
    paper_data = {
        "title": "Paper with DOI",
        "authors": "Test Author",
        "doi": "10.1000/test.doi.123",
        "tag_ids": [],
    }
    create_response = client.post("/api/v1/papers/", json=paper_data)
    assert create_response.status_code == 200

    # DOIで取得
    response = client.get("/api/v1/papers/doi/10.1000/test.doi.123")
    assert response.status_code == 200
    data = response.json()
    assert data["doi"] == "10.1000/test.doi.123"
    assert data["title"] == "Paper with DOI"


def test_正常系_お気に入り論文一覧(client: TestClient):
    """お気に入り論文の一覧が正常に取得できることを確認."""
    # お気に入り論文を作成
    paper_data = {
        "title": "Favorite Paper",
        "authors": "Test Author",
        "is_favorite": True,
        "tag_ids": [],
    }
    create_response = client.post("/api/v1/papers/", json=paper_data)
    assert create_response.status_code == 200

    # お気に入り一覧を取得
    response = client.get("/api/v1/papers/favorites")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # 作成した論文がお気に入り一覧に含まれることを確認
    favorite_titles = [paper["title"] for paper in data]
    assert "Favorite Paper" in favorite_titles


def test_正常系_被引用数増加(client: TestClient):
    """被引用数が正常に増加することを確認."""
    # 論文を作成
    paper_data = {
        "title": "Paper to Cite",
        "authors": "Test Author",
        "citation_count": 0,
        "tag_ids": [],
    }
    create_response = client.post("/api/v1/papers/", json=paper_data)
    paper_id = create_response.json()["id"]

    # 被引用数を増加
    response = client.post(f"/api/v1/papers/{paper_id}/cite")
    assert response.status_code == 200
    data = response.json()
    assert data["citation_count"] == 1


def test_正常系_論文削除(client: TestClient):
    """論文が正常に削除できることを確認."""
    # まず論文を作成
    paper_data = {
        "title": "Paper to Delete",
        "authors": "Test Author",
        "tag_ids": [],
    }
    create_response = client.post("/api/v1/papers/", json=paper_data)
    paper_id = create_response.json()["id"]

    # 削除
    response = client.delete(f"/api/v1/papers/{paper_id}")
    assert response.status_code == 200

    # 削除後に取得を試みる
    get_response = client.get(f"/api/v1/papers/{paper_id}")
    assert get_response.status_code == 404


def test_異常系_存在しない論文取得(client: TestClient):
    """存在しない論文の取得で404エラーが返されることを確認."""
    response = client.get("/api/v1/papers/99999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]


def test_異常系_無効な評価値(client: TestClient):
    """無効な評価値で400エラーが返されることを確認."""
    # まず論文を作成
    paper_data = {
        "title": "Paper for Invalid Rating",
        "authors": "Test Author",
        "tag_ids": [],
    }
    create_response = client.post("/api/v1/papers/", json=paper_data)
    paper_id = create_response.json()["id"]

    # 無効な評価値を設定
    rating_data = {"rating": 6}  # 1-5の範囲外
    response = client.post(f"/api/v1/papers/{paper_id}/rating", json=rating_data)
    assert response.status_code == 422  # Validation error


def test_異常系_重複DOI(client: TestClient):
    """重複するDOIで論文作成時に400エラーが返されることを確認."""
    # 最初の論文を作成
    paper_data1 = {
        "title": "First Paper",
        "authors": "Author One",
        "doi": "10.1000/duplicate.doi",
        "tag_ids": [],
    }
    response1 = client.post("/api/v1/papers/", json=paper_data1)
    assert response1.status_code == 200

    # 同じDOIで2番目の論文を作成を試みる
    paper_data2 = {
        "title": "Second Paper",
        "authors": "Author Two",
        "doi": "10.1000/duplicate.doi",
        "tag_ids": [],
    }
    response2 = client.post("/api/v1/papers/", json=paper_data2)
    assert response2.status_code == 400
    data = response2.json()
    assert "already exists" in data["detail"]
