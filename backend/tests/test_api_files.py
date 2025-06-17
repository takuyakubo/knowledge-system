"""Tests for File Upload API endpoints."""

import io

from fastapi.testclient import TestClient


def test_正常系_ファイル一覧取得(client: TestClient):
    """ファイル一覧が正常に取得できることを確認."""
    response = client.get("/api/v1/files/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_正常系_画像アップロード(client: TestClient):
    """画像ファイルのアップロードが正常に実行できることを確認."""
    # テスト用の画像データを作成
    image_data = b"fake_image_data"
    files = {"file": ("test.jpg", io.BytesIO(image_data), "image/jpeg")}
    data = {
        "description": "テスト画像",
        "alt_text": "テスト用の画像",
        "is_public": "true",  # フォーム送信では文字列
    }

    response = client.post("/api/v1/files/upload", files=files, data=data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["filename"] == "test.jpg"
    assert response_data["file_type"] == "image"
    assert response_data["mime_type"] == "image/jpeg"
    assert "url" in response_data
    assert response_data["is_image"] is True
    return response_data["file_id"]


def test_正常系_ドキュメントアップロード(client: TestClient):
    """ドキュメントファイルのアップロードが正常に実行できることを確認."""
    # テスト用のPDFデータを作成
    pdf_data = b"fake_pdf_data"
    files = {"file": ("document.pdf", io.BytesIO(pdf_data), "application/pdf")}
    data = {
        "description": "テストドキュメント",
        "is_public": "true",
    }

    response = client.post("/api/v1/files/upload", files=files, data=data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["filename"] == "document.pdf"
    assert response_data["file_type"] == "pdf"
    assert response_data["mime_type"] == "application/pdf"
    assert "url" in response_data
    return response_data["file_id"]


def test_正常系_ファイル詳細取得(client: TestClient):
    """ファイル詳細が正常に取得できることを確認."""
    # まずファイルをアップロード
    image_data = b"test_data_for_detail"
    files = {"file": ("detail_test.png", io.BytesIO(image_data), "image/png")}
    upload_response = client.post("/api/v1/files/upload", files=files)
    file_id = upload_response.json()["file_id"]

    # 詳細を取得
    response = client.get(f"/api/v1/files/{file_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == file_id
    assert data["filename"] == "detail_test.png"
    assert data["file_type"] == "image"


def test_正常系_ファイル情報更新(client: TestClient):
    """ファイル情報が正常に更新できることを確認."""
    # ファイルをアップロード
    image_data = b"update_test_data"
    files = {"file": ("update_test.jpg", io.BytesIO(image_data), "image/jpeg")}
    upload_response = client.post("/api/v1/files/upload", files=files)
    file_id = upload_response.json()["file_id"]

    # 情報を更新
    update_data = {
        "description": "更新された説明",
        "alt_text": "更新された代替テキスト",
    }
    response = client.put(f"/api/v1/files/{file_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == update_data["description"]
    assert data["alt_text"] == update_data["alt_text"]


def test_正常系_画像ファイル一覧取得(client: TestClient):
    """画像ファイルの一覧が正常に取得できることを確認."""
    response = client.get("/api/v1/files/images")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # 全て画像ファイルであることを確認
    for file_data in data:
        assert file_data["file_type"] == "image"


def test_正常系_ドキュメントファイル一覧取得(client: TestClient):
    """ドキュメントファイルの一覧が正常に取得できることを確認."""
    response = client.get("/api/v1/files/documents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # 全てドキュメント・PDFファイルであることを確認
    for file_data in data:
        assert file_data["file_type"] in ["document", "pdf"]


def test_正常系_ファイルタイプ別取得(client: TestClient):
    """指定タイプのファイルが正常に取得できることを確認."""
    response = client.get("/api/v1/files/types/image")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for file_data in data:
        assert file_data["file_type"] == "image"


def test_正常系_ファイル検索(client: TestClient):
    """ファイル検索が正常に実行できることを確認."""
    # 検索用ファイルをアップロード
    search_data = b"search_test_data"
    files = {"file": ("searchable.txt", io.BytesIO(search_data), "text/plain")}
    data = {"description": "検索テスト用ファイル"}
    client.post("/api/v1/files/upload", files=files, data=data)

    # 検索実行
    response = client.get("/api/v1/files/search?q=searchable")
    assert response.status_code == 200
    search_result = response.json()
    assert "files" in search_result
    assert "total" in search_result
    assert "page" in search_result


def test_正常系_ファイル統計取得(client: TestClient):
    """ファイル統計情報が正常に取得できることを確認."""
    response = client.get("/api/v1/files/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_files" in data
    assert "total_size" in data
    assert "total_size_readable" in data
    assert "by_type" in data
    assert "by_extension" in data
    assert "average_size" in data


def test_正常系_複数ファイルアップロード(client: TestClient):
    """複数ファイルの一括アップロードが正常に実行できることを確認."""
    # 複数のテストファイルを作成
    files = [
        ("files", ("bulk1.jpg", io.BytesIO(b"bulk_test_1"), "image/jpeg")),
        ("files", ("bulk2.png", io.BytesIO(b"bulk_test_2"), "image/png")),
    ]
    data = {"is_public": "true"}

    response = client.post("/api/v1/files/upload/bulk", files=files, data=data)
    assert response.status_code == 200
    response_data = response.json()
    assert "uploaded_files" in response_data
    assert "failed_files" in response_data
    assert "total_files" in response_data
    assert "success_count" in response_data
    assert "failure_count" in response_data
    assert response_data["total_files"] == 2


def test_正常系_記事との関連付け(client: TestClient):
    """ファイルと記事の関連付けが正常に実行できることを確認."""
    # ファイルをアップロード
    file_data = b"association_test"
    files = {"file": ("association.jpg", io.BytesIO(file_data), "image/jpeg")}
    upload_response = client.post("/api/v1/files/upload", files=files)
    file_id = upload_response.json()["file_id"]

    # 仮の記事IDで関連付け（実際の記事は存在しないが、エンドポイントの動作確認）
    article_id = 1
    response = client.post(f"/api/v1/files/{file_id}/associate/article/{article_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["article_id"] == article_id


def test_正常系_論文との関連付け(client: TestClient):
    """ファイルと論文の関連付けが正常に実行できることを確認."""
    # ファイルをアップロード
    file_data = b"paper_association_test"
    files = {"file": ("paper_file.pdf", io.BytesIO(file_data), "application/pdf")}
    upload_response = client.post("/api/v1/files/upload", files=files)
    file_id = upload_response.json()["file_id"]

    # 仮の論文IDで関連付け
    paper_id = 1
    response = client.post(f"/api/v1/files/{file_id}/associate/paper/{paper_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["paper_id"] == paper_id


def test_正常系_関連付け解除(client: TestClient):
    """ファイルの関連付け解除が正常に実行できることを確認."""
    # ファイルをアップロード
    file_data = b"remove_association_test"
    files = {"file": ("remove_assoc.jpg", io.BytesIO(file_data), "image/jpeg")}
    upload_response = client.post("/api/v1/files/upload", files=files)
    file_id = upload_response.json()["file_id"]

    # 関連付け解除
    response = client.delete(f"/api/v1/files/{file_id}/associations")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_正常系_一括公開設定更新(client: TestClient):
    """複数ファイルの公開設定一括更新が正常に実行できることを確認."""
    # 複数ファイルをアップロード
    file_ids = []
    for i in range(2):
        file_data = f"bulk_visibility_{i}".encode()
        files = {"file": (f"bulk_vis_{i}.txt", io.BytesIO(file_data), "text/plain")}
        upload_response = client.post("/api/v1/files/upload", files=files)
        file_ids.append(upload_response.json()["file_id"])

    # 一括で非公開に設定
    update_data = {"file_ids": file_ids, "is_public": False}
    response = client.post("/api/v1/files/bulk/visibility", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    for file_data in data:
        assert file_data["is_public"] is False


def test_正常系_フィルター付きファイル取得(client: TestClient):
    """フィルター条件付きでファイルが正常に取得できることを確認."""
    # 画像ファイルのみ取得
    response = client.get("/api/v1/files/?file_type=image")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for file_data in data:
        assert file_data["file_type"] == "image"

    # 公開ファイルのみ取得
    response = client.get("/api/v1/files/?is_public=true")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for file_data in data:
        assert file_data["is_public"] is True


def test_正常系_人気ファイル取得(client: TestClient):
    """人気ファイルが正常に取得できることを確認."""
    response = client.get("/api/v1/files/popular")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_異常系_存在しないファイル取得(client: TestClient):
    """存在しないファイルの取得で404エラーが返されることを確認."""
    response = client.get("/api/v1/files/99999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_異常系_無効なファイル形式アップロード(client: TestClient):
    """許可されていないファイル形式のアップロードで400エラーが返されることを確認."""
    # 許可されていない拡張子のファイル
    invalid_data = b"invalid_file_data"
    files = {
        "file": ("invalid.xyz", io.BytesIO(invalid_data), "application/octet-stream")
    }

    response = client.post("/api/v1/files/upload", files=files)
    assert response.status_code == 400
    data = response.json()
    assert "許可されていない" in data["detail"]


def test_異常系_空のファイルアップロード(client: TestClient):
    """ファイル名が空の場合に400エラーが返されることを確認."""
    files = {"file": ("", io.BytesIO(b"data"), "text/plain")}

    response = client.post("/api/v1/files/upload", files=files)
    assert response.status_code == 400
    data = response.json()
    assert "ファイル名が必要" in data["detail"]


def test_異常系_存在しないファイルダウンロード(client: TestClient):
    """存在しないファイルのダウンロードで404エラーが返されることを確認."""
    response = client.get("/api/v1/files/99999/download")
    assert response.status_code == 404


def test_エッジケース_空の検索クエリ(client: TestClient):
    """空の検索クエリで400エラーが返されることを確認."""
    response = client.get("/api/v1/files/search?q=")
    assert response.status_code == 422  # バリデーションエラー（min_length=1）


def test_エッジケース_重複ファイルアップロード(client: TestClient):
    """同一内容のファイルを複数回アップロードした場合の動作確認."""
    # 同じ内容のファイルを2回アップロード
    same_data = b"duplicate_test_data"
    files1 = {"file": ("dup1.txt", io.BytesIO(same_data), "text/plain")}
    files2 = {"file": ("dup2.txt", io.BytesIO(same_data), "text/plain")}

    response1 = client.post("/api/v1/files/upload", files=files1)
    response2 = client.post("/api/v1/files/upload", files=files2)

    # 両方とも成功するが、同じfile_idが返される（重複検出）
    assert response1.status_code == 200
    assert response2.status_code == 200

    file_id1 = response1.json()["file_id"]
    file_id2 = response2.json()["file_id"]
    assert file_id1 == file_id2  # 同じハッシュなので同じID
