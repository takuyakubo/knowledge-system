"""API compatibility and versioning tests."""

import io

from fastapi.testclient import TestClient


class TestAPIVersioning:
    """API バージョニングとの互換性テスト."""

    def test_api_v1_endpoints_availability(self, client: TestClient):
        """v1 API エンドポイントの可用性をテスト."""
        # すべての主要エンドポイントが利用可能であることを確認
        endpoints = [
            "/api/v1/articles/",
            "/api/v1/papers/",
            "/api/v1/tags/",
            "/api/v1/categories/",
            "/api/v1/files/",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert (
                response.status_code == 200
            ), f"エンドポイント {endpoint} が利用できません"
            assert isinstance(
                response.json(), list
            ), f"エンドポイント {endpoint} のレスポンス形式が正しくありません"

    def test_response_schema_consistency(self, client: TestClient):
        """レスポンススキーマの一貫性をテスト."""
        # 記事作成とレスポンス確認
        article_data = {
            "title": "Schema Test Article",
            "content": "Testing response schema consistency",
            "status": "published",
        }

        create_response = client.post("/api/v1/articles/", json=article_data)
        assert create_response.status_code == 200
        created_article = create_response.json()

        # 必須フィールドの存在確認
        required_fields = [
            "id",
            "title",
            "content",
            "status",
            "created_at",
            "updated_at",
        ]
        for field in required_fields:
            assert (
                field in created_article
            ), f"必須フィールド '{field}' が不足しています"

        # 取得時のスキーマ一貫性確認
        get_response = client.get(f"/api/v1/articles/{created_article['id']}")
        assert get_response.status_code == 200
        retrieved_article = get_response.json()

        # 同じ構造であることを確認
        for field in required_fields:
            assert (
                field in retrieved_article
            ), f"取得時に必須フィールド '{field}' が不足しています"
            assert isinstance(
                created_article[field], type(retrieved_article[field])
            ), f"フィールド '{field}' の型が不一致です"

    def test_error_response_consistency(self, client: TestClient):
        """エラーレスポンスの一貫性をテスト."""
        # 存在しないリソースへのアクセス
        not_found_endpoints = [
            "/api/v1/articles/99999",
            "/api/v1/papers/99999",
            "/api/v1/tags/99999",
            "/api/v1/categories/99999",
            "/api/v1/files/99999",
        ]

        for endpoint in not_found_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 404
            error_data = response.json()
            assert (
                "detail" in error_data
            ), f"エラーレスポンスに 'detail' フィールドがありません: {endpoint}"

    def test_pagination_consistency(self, client: TestClient):
        """ページネーションの一貫性をテスト."""
        # テストデータ準備
        for i in range(15):
            client.post(
                "/api/v1/articles/",
                json={
                    "title": f"Pagination Test {i}",
                    "content": f"Content {i}",
                    "status": "published",
                },
            )

        # ページネーションパラメータのテスト
        pagination_endpoints = [
            "/api/v1/articles/",
            "/api/v1/tags/",
            "/api/v1/categories/",
            "/api/v1/files/",
        ]

        for endpoint in pagination_endpoints:
            # デフォルトパラメータ
            response = client.get(endpoint)
            assert response.status_code == 200

            # skip/limit パラメータ
            response = client.get(f"{endpoint}?skip=5&limit=5")
            assert response.status_code == 200
            data = response.json()
            assert (
                len(data) <= 5
            ), f"limit パラメータが正しく動作していません: {endpoint}"


class TestBackwardCompatibility:
    """後方互換性テスト."""

    def test_required_fields_preservation(self, client: TestClient):
        """必須フィールドが保持されていることをテスト."""
        # 記事の必須フィールド
        article_data = {
            "title": "Backward Compatibility Test",
            "content": "Test content",
        }
        response = client.post("/api/v1/articles/", json=article_data)
        assert response.status_code == 200

        article = response.json()
        legacy_required_fields = ["id", "title", "content", "created_at"]
        for field in legacy_required_fields:
            assert (
                field in article
            ), f"レガシー必須フィールド '{field}' が不足しています"

    def test_optional_fields_handling(self, client: TestClient):
        """オプションフィールドの適切な処理をテスト."""
        # 最小限のデータで作成
        minimal_data = {"title": "Minimal Article", "content": "Minimal content"}
        response = client.post("/api/v1/articles/", json=minimal_data)
        assert response.status_code == 200

        article = response.json()

        # オプションフィールドがデフォルト値またはnullで設定されていることを確認
        optional_fields = {
            "excerpt": None,
            "status": "draft",  # デフォルト値
            "is_featured": False,
            "category_id": None,
            "tag_ids": [],
        }

        for field, expected_default in optional_fields.items():
            assert field in article, f"オプションフィールド '{field}' が不足しています"
            if expected_default is not None:
                assert (
                    article[field] == expected_default
                ), f"オプションフィールド '{field}' のデフォルト値が正しくありません"

    def test_field_type_consistency(self, client: TestClient):
        """フィールドタイプの一貫性をテスト."""
        # カテゴリ作成
        category_data = {"name": "Type Test Category"}
        cat_response = client.post("/api/v1/categories/", json=category_data)
        category_id = cat_response.json()["id"]

        # タグ作成
        tag_data = {"name": "Type Test Tag"}
        tag_response = client.post("/api/v1/tags/", json=tag_data)
        tag_id = tag_response.json()["id"]

        # 記事作成（全フィールド指定）
        full_article_data = {
            "title": "Type Consistency Test",
            "content": "Testing field types",
            "excerpt": "Test excerpt",
            "status": "published",
            "is_featured": True,
            "category_id": category_id,
            "tag_ids": [tag_id],
            "reading_time": 5,
        }

        response = client.post("/api/v1/articles/", json=full_article_data)
        assert response.status_code == 200
        article = response.json()

        # フィールドタイプの確認
        type_expectations = {
            "id": int,
            "title": str,
            "content": str,
            "excerpt": str,
            "status": str,
            "is_featured": bool,
            "category_id": int,
            "tag_ids": list,
            "reading_time": int,
        }

        for field, expected_type in type_expectations.items():
            assert isinstance(article[field], expected_type), (
                f"フィールド '{field}' の型が期待値 {expected_type} と異なります: "
                f"{type(article[field])}"
            )


class TestCrossAPIIntegration:
    """異なるAPI間の統合テスト."""

    def test_cross_reference_integrity(self, client: TestClient):
        """異なるエンティティ間の参照整合性をテスト."""
        # 1. 基本エンティティ作成
        category = client.post(
            "/api/v1/categories/", json={"name": "Integration Test"}
        ).json()
        tag = client.post("/api/v1/tags/", json={"name": "Integration Tag"}).json()

        # 2. 記事作成（カテゴリ・タグ参照）
        article_data = {
            "title": "Cross Reference Test",
            "content": "Testing cross-references",
            "category_id": category["id"],
            "tag_ids": [tag["id"]],
            "status": "published",
        }
        client.post("/api/v1/articles/", json=article_data)

        # 3. 論文作成（同じカテゴリ・タグ参照）
        paper_data = {
            "title": "Cross Reference Paper",
            "authors": "Test Author",
            "category_id": category["id"],
            "tag_ids": [tag["id"]],
        }
        client.post("/api/v1/papers/", json=paper_data)

        # 4. 参照整合性確認
        # カテゴリから記事・論文への参照
        category_detail = client.get(f"/api/v1/categories/{category['id']}").json()
        assert category_detail["article_count"] >= 1
        assert category_detail["paper_count"] >= 1

        # タグの使用統計確認
        tag_stats = client.get("/api/v1/tags/usage-stats").json()
        integration_tag_stats = next(
            (stats for stats in tag_stats if stats["tag_id"] == tag["id"]), None
        )
        assert integration_tag_stats is not None
        assert integration_tag_stats["usage_count"] >= 2  # 記事と論文で使用

    def test_batch_operations_across_apis(self, client: TestClient):
        """複数API間での一括操作をテスト."""
        # 1. 一括タグ作成
        tag_names = ["Batch1", "Batch2", "Batch3"]
        bulk_tags = client.post(
            "/api/v1/tags/bulk-create", json={"tag_names": tag_names}
        ).json()
        tag_ids = [tag["id"] for tag in bulk_tags["created_tags"]]

        # 2. カテゴリ作成
        category = client.post(
            "/api/v1/categories/", json={"name": "Batch Test"}
        ).json()

        # 3. 複数記事作成（一括タグ使用）
        articles = []
        for i in range(3):
            article_data = {
                "title": f"Batch Article {i}",
                "content": f"Batch content {i}",
                "category_id": category["id"],
                "tag_ids": tag_ids,
                "status": "published",
            }
            article = client.post("/api/v1/articles/", json=article_data).json()
            articles.append(article)

        # 4. 一括ファイルアップロード
        files = [
            ("files", (f"batch_{i}.txt", io.BytesIO(b"batch content"), "text/plain"))
            for i in range(3)
        ]
        bulk_files = client.post("/api/v1/files/upload/bulk", files=files).json()
        file_ids = [f["file_id"] for f in bulk_files["uploaded_files"]]

        # 5. ファイルと記事の関連付け
        for article, file_id in zip(articles, file_ids, strict=False):
            response = client.post(
                f"/api/v1/files/{file_id}/associate/article/{article['id']}"
            )
            assert response.status_code == 200

        # 6. 統計確認
        # タグ使用統計
        tag_usage = client.get("/api/v1/tags/usage-stats").json()
        for tag_id in tag_ids:
            tag_stat = next(
                (stat for stat in tag_usage if stat["tag_id"] == tag_id), None
            )
            assert tag_stat is not None
            assert tag_stat["usage_count"] >= 3  # 3記事で使用

        # ファイル統計
        file_stats = client.get("/api/v1/files/stats").json()
        assert file_stats["total_files"] >= 3

    def test_search_across_all_entities(self, client: TestClient):
        """全エンティティ横断検索をテスト."""
        search_term = "CrossSearch"

        # 1. 各エンティティに検索用データを作成
        article_data = {
            "title": f"{search_term} Article",
            "content": f"Content with {search_term}",
            "status": "published",
        }
        client.post("/api/v1/articles/", json=article_data)

        paper_data = {
            "title": f"{search_term} Paper",
            "authors": "Search Author",
            "abstract": f"Abstract with {search_term}",
        }
        client.post("/api/v1/papers/", json=paper_data)

        tag_data = {
            "name": f"{search_term}Tag",
            "description": f"Tag for {search_term}",
        }
        client.post("/api/v1/tags/", json=tag_data)

        category_data = {
            "name": f"{search_term}Category",
            "description": f"Category for {search_term}",
        }
        client.post("/api/v1/categories/", json=category_data)

        # 2. 各エンティティでの検索実行
        search_endpoints = [
            f"/api/v1/articles/search?q={search_term}",
            f"/api/v1/papers/search?q={search_term}",
            f"/api/v1/tags/search?q={search_term}",
            f"/api/v1/categories/search?q={search_term}",
        ]

        for endpoint in search_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200

            # レスポンス構造の確認
            data = response.json()
            if "articles" in data:
                assert len(data["articles"]) >= 1
            elif "papers" in data:
                assert len(data["papers"]) >= 1
            elif "tags" in data:
                assert len(data["tags"]) >= 1
            elif "categories" in data:
                assert len(data["categories"]) >= 1
            else:
                # 直接リストの場合
                assert isinstance(data, list)
                assert len(data) >= 1
