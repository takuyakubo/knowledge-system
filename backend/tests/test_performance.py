"""Performance and load testing for API endpoints."""

import io
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi.testclient import TestClient


class TestAPIPerformance:
    """API パフォーマンステスト."""

    def test_大量データ作成のパフォーマンス(self, client: TestClient):
        """大量のデータ作成時のパフォーマンスをテスト."""
        start_time = time.time()

        # 1. 大量タグの一括作成
        tag_names = [f"Tag_{i}" for i in range(50)]
        bulk_tags_data = {"tag_names": tag_names}
        response = client.post("/api/v1/tags/bulk-create", json=bulk_tags_data)
        assert response.status_code == 200
        created_tags = response.json()["created_tags"]
        assert len(created_tags) == 50

        # 2. 複数カテゴリの作成
        categories = []
        for i in range(10):
            category_data = {"name": f"Category_{i}", "description": f"Description {i}"}
            response = client.post("/api/v1/categories/", json=category_data)
            assert response.status_code == 200
            categories.append(response.json())

        # 3. 大量記事の作成
        articles = []
        tag_ids = [tag["id"] for tag in created_tags[:10]]  # 最初の10個のタグを使用

        for i in range(20):
            article_data = {
                "title": f"Performance Test Article {i}",
                "content": f"Content for article {i} " * 100,  # 長いコンテンツ
                "category_id": categories[i % len(categories)]["id"],
                "tag_ids": tag_ids[:3],  # 3つのタグを関連付け
                "status": "published",
            }
            response = client.post("/api/v1/articles/", json=article_data)
            assert response.status_code == 200
            articles.append(response.json())

        end_time = time.time()
        creation_time = end_time - start_time

        # 作成時間が合理的な範囲内であることを確認（10秒以内）
        assert (
            creation_time < 10.0
        ), f"大量データ作成に{creation_time:.2f}秒かかりました"

        print(f"大量データ作成時間: {creation_time:.2f}秒")

    def test_検索パフォーマンス(self, client: TestClient):
        """検索機能のパフォーマンスをテスト."""
        # 検索用データの準備
        category_response = client.post(
            "/api/v1/categories/", json={"name": "Search Test"}
        )
        category_id = category_response.json()["id"]

        # 複数記事を作成
        for i in range(30):
            article_data = {
                "title": f"検索テスト記事 {i}",
                "content": f"検索用のコンテンツです。キーワード: test_keyword_{i}",
                "category_id": category_id,
                "status": "published",
            }
            client.post("/api/v1/articles/", json=article_data)

        # 検索パフォーマンステスト
        start_time = time.time()

        search_queries = ["検索テスト", "test_keyword", "記事", "コンテンツ"]
        for query in search_queries:
            response = client.get(f"/api/v1/articles/search?q={query}&limit=10")
            assert response.status_code == 200
            results = response.json()
            assert "articles" in results

        end_time = time.time()
        search_time = end_time - start_time

        # 検索時間が1秒以内であることを確認
        assert search_time < 1.0, f"検索処理に{search_time:.2f}秒かかりました"

        print(f"検索パフォーマンス: {search_time:.2f}秒 (4クエリ)")

    def test_ファイルアップロードパフォーマンス(self, client: TestClient):
        """ファイルアップロードのパフォーマンスをテスト."""
        # 中程度サイズのファイルを作成（1MB）
        large_content = b"x" * (1024 * 1024)  # 1MB

        start_time = time.time()

        # 5つのファイルを連続アップロード
        file_ids = []
        for i in range(5):
            files = {
                "file": (f"large_file_{i}.txt", io.BytesIO(large_content), "text/plain")
            }
            response = client.post("/api/v1/files/upload", files=files)
            assert response.status_code == 200
            file_ids.append(response.json()["file_id"])

        end_time = time.time()
        upload_time = end_time - start_time

        # アップロード時間が合理的な範囲内であることを確認（5秒以内）
        assert (
            upload_time < 5.0
        ), f"ファイルアップロードに{upload_time:.2f}秒かかりました"

        print(f"ファイルアップロード時間: {upload_time:.2f}秒 (5MB合計)")

    def test_ページネーション性能(self, client: TestClient):
        """ページネーション機能の性能をテスト."""
        # テスト用データ準備（50記事）
        category_response = client.post(
            "/api/v1/categories/", json={"name": "Pagination Test"}
        )
        category_id = category_response.json()["id"]

        for i in range(50):
            article_data = {
                "title": f"Pagination Test Article {i:03d}",
                "content": f"Content {i}",
                "category_id": category_id,
                "status": "published",
            }
            client.post("/api/v1/articles/", json=article_data)

        # ページネーション性能テスト
        start_time = time.time()

        # 5ページ分のデータを取得
        for page in range(5):
            skip = page * 10
            response = client.get(f"/api/v1/articles/?skip={skip}&limit=10")
            assert response.status_code == 200
            articles = response.json()
            assert len(articles) == 10

        end_time = time.time()
        pagination_time = end_time - start_time

        # ページネーション時間が1秒以内であることを確認
        assert (
            pagination_time < 1.0
        ), f"ページネーション処理に{pagination_time:.2f}秒かかりました"

        print(f"ページネーション性能: {pagination_time:.2f}秒 (50記事, 5ページ)")


class TestConcurrencyAndStress:
    """並行処理とストレステスト."""

    def test_並行記事作成(self, client: TestClient):
        """複数の並行記事作成をテスト."""
        # カテゴリ準備
        category_response = client.post(
            "/api/v1/categories/", json={"name": "Concurrency Test"}
        )
        category_id = category_response.json()["id"]

        def create_article(index):
            """記事作成ヘルパー関数."""
            article_data = {
                "title": f"並行作成記事 {index}",
                "content": f"並行処理テスト用コンテンツ {index}",
                "category_id": category_id,
                "status": "published",
            }
            response = client.post("/api/v1/articles/", json=article_data)
            return (
                response.status_code,
                response.json() if response.status_code == 200 else None,
            )

        # 10個の記事を並行作成
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_article, i) for i in range(10)]
            results = []

            for future in as_completed(futures):
                status_code, data = future.result()
                results.append((status_code, data))

        end_time = time.time()
        concurrent_time = end_time - start_time

        # 全ての作成が成功したことを確認
        successful_creations = sum(1 for status, _ in results if status == 200)
        assert (
            successful_creations == 10
        ), f"並行作成で{successful_creations}/10個の記事が作成されました"

        print(f"並行記事作成時間: {concurrent_time:.2f}秒 (10記事)")

    def test_大量データ取得性能(self, client: TestClient):
        """大量データ取得時の性能をテスト."""
        # 大量データの準備は前のテストで作成されていることを前提

        start_time = time.time()

        # 様々なエンドポイントから大量データを取得
        endpoints = [
            "/api/v1/articles/?limit=100",
            "/api/v1/categories/",
            "/api/v1/tags/?limit=100",
            "/api/v1/files/?limit=50",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

        end_time = time.time()
        retrieval_time = end_time - start_time

        # データ取得時間が2秒以内であることを確認
        assert (
            retrieval_time < 2.0
        ), f"大量データ取得に{retrieval_time:.2f}秒かかりました"

        print(f"大量データ取得時間: {retrieval_time:.2f}秒")

    def test_重複ファイル処理性能(self, client: TestClient):
        """重複ファイル検出の性能をテスト."""
        # 同一内容のファイルを複数回アップロード
        file_content = b"duplicate_test_content" * 1000  # 約24KB

        start_time = time.time()

        file_ids = []
        for i in range(10):
            files = {
                "file": (f"duplicate_{i}.txt", io.BytesIO(file_content), "text/plain")
            }
            response = client.post("/api/v1/files/upload", files=files)
            assert response.status_code == 200
            file_ids.append(response.json()["file_id"])

        end_time = time.time()
        dedup_time = end_time - start_time

        # 全て同じfile_idが返されることを確認（重複検出）
        unique_ids = set(file_ids)
        assert len(unique_ids) == 1, "重複ファイル検出が正しく動作していません"

        print(f"重複ファイル処理時間: {dedup_time:.2f}秒 (10回アップロード)")


class TestDataIntegrity:
    """データ整合性とトランザクション性能テスト."""

    def test_トランザクション整合性(self, client: TestClient):
        """複雑な操作でのデータ整合性をテスト."""
        # 1. 初期データ作成
        category_response = client.post(
            "/api/v1/categories/", json={"name": "Transaction Test"}
        )
        category_id = category_response.json()["id"]

        tag_response = client.post("/api/v1/tags/", json={"name": "Transaction Tag"})
        tag_id = tag_response.json()["id"]

        # 2. 記事作成
        article_data = {
            "title": "Transaction Test Article",
            "content": "Transaction test content",
            "category_id": category_id,
            "tag_ids": [tag_id],
            "status": "published",
        }
        article_response = client.post("/api/v1/articles/", json=article_data)
        article_id = article_response.json()["id"]

        # 3. ファイル作成と関連付け
        files = {
            "file": ("transaction_test.txt", io.BytesIO(b"test_content"), "text/plain")
        }
        file_response = client.post("/api/v1/files/upload", files=files)
        file_id = file_response.json()["file_id"]

        associate_response = client.post(
            f"/api/v1/files/{file_id}/associate/article/{article_id}"
        )
        assert associate_response.status_code == 200

        # 4. データ整合性確認
        article_detail = client.get(f"/api/v1/articles/{article_id}").json()
        assert article_detail["category_id"] == category_id
        assert tag_id in article_detail["tag_ids"]

        file_detail = client.get(f"/api/v1/files/{file_id}").json()
        assert file_detail["article_id"] == article_id

        # 5. カテゴリ統計の一貫性確認
        category_detail = client.get(f"/api/v1/categories/{category_id}").json()
        assert category_detail["article_count"] >= 1

        print("データ整合性テスト完了")

    def test_大量関連付け処理(self, client: TestClient):
        """大量の関連付け処理の性能をテスト."""
        # 1. 基本データ準備
        category_response = client.post(
            "/api/v1/categories/", json={"name": "Bulk Relations"}
        )
        category_id = category_response.json()["id"]

        # 2. 20個のタグを作成
        tag_ids = []
        for i in range(20):
            tag_response = client.post("/api/v1/tags/", json={"name": f"Bulk Tag {i}"})
            tag_ids.append(tag_response.json()["id"])

        start_time = time.time()

        # 3. 10個の記事に全タグを関連付け
        article_ids = []
        for i in range(10):
            article_data = {
                "title": f"Bulk Relations Article {i}",
                "content": f"Content {i}",
                "category_id": category_id,
                "tag_ids": tag_ids,  # 全20個のタグを関連付け
                "status": "published",
            }
            response = client.post("/api/v1/articles/", json=article_data)
            assert response.status_code == 200
            article_ids.append(response.json()["id"])

        end_time = time.time()
        bulk_relation_time = end_time - start_time

        # 関連付け処理時間が5秒以内であることを確認
        assert (
            bulk_relation_time < 5.0
        ), f"大量関連付け処理に{bulk_relation_time:.2f}秒かかりました"

        # データ確認
        for article_id in article_ids:
            article_detail = client.get(f"/api/v1/articles/{article_id}").json()
            assert len(article_detail["tag_ids"]) == 20

        print(f"大量関連付け処理時間: {bulk_relation_time:.2f}秒 (10記事 x 20タグ)")


class TestErrorHandlingAndRecovery:
    """エラーハンドリングと回復性テスト."""

    def test_不正データでのロバスト性(self, client: TestClient):
        """不正なデータに対するシステムのロバスト性をテスト."""
        # 1. 非常に長いタイトルでの作成試行
        long_title = "A" * 1000  # 非常に長いタイトル
        article_data = {
            "title": long_title,
            "content": "Normal content",
            "status": "published",
        }
        response = client.post("/api/v1/articles/", json=article_data)
        # バリデーションエラーまたは正常処理のいずれかが期待される
        assert response.status_code in [200, 422]

        # 2. 無効なファイル形式での大量アップロード試行
        invalid_files = []
        for i in range(5):
            invalid_files.append(
                (
                    "files",
                    (
                        f"invalid_{i}.exe",
                        io.BytesIO(b"malicious_content"),
                        "application/x-executable",
                    ),
                )
            )

        response = client.post("/api/v1/files/upload/bulk", files=invalid_files)
        assert response.status_code == 200  # 一部失敗は許容される
        result = response.json()
        assert result["failure_count"] == 5  # 全て失敗するはず

        # 3. 存在しないIDでの大量操作試行
        non_existent_ids = [99999, 99998, 99997]
        visibility_data = {"file_ids": non_existent_ids, "is_public": False}
        response = client.post("/api/v1/files/bulk/visibility", json=visibility_data)
        # エラーハンドリングされることを確認
        assert response.status_code in [200, 404, 400]

        print("ロバスト性テスト完了")

    def test_リソース制限処理(self, client: TestClient):
        """リソース制限に対する適切な処理をテスト."""
        # 1. 大量データ取得での制限テスト
        response = client.get("/api/v1/articles/?limit=10000")  # 非常に大きなlimit
        assert response.status_code == 422  # バリデーションエラー

        # 2. 非常に大きなページネーション
        response = client.get("/api/v1/articles/?skip=1000000&limit=100")
        assert response.status_code == 200  # 処理は成功するが空の結果
        articles = response.json()
        assert len(articles) == 0

        print("リソース制限テスト完了")
