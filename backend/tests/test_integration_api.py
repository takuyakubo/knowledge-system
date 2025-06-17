"""Integration tests for API endpoints - testing workflows and entity relationships."""

import io

from fastapi.testclient import TestClient


class TestArticleWorkflow:
    """記事関連のワークフロー統合テスト."""

    def test_完全な記事作成ワークフロー(self, client: TestClient):
        """記事作成から公開までの完全なワークフローをテスト."""
        # 1. カテゴリを作成
        category_data = {
            "name": "Technology",
            "description": "Technology articles",
            "color": "#3498db",
        }
        category_response = client.post("/api/v1/categories/", json=category_data)
        assert category_response.status_code == 200
        category_id = category_response.json()["id"]

        # 2. タグを作成
        tag_data = {"name": "Python", "description": "Python programming"}
        tag_response = client.post("/api/v1/tags/", json=tag_data)
        assert tag_response.status_code == 200
        tag_id = tag_response.json()["id"]

        # 3. ファイルをアップロード
        image_data = b"fake_image_content"
        files = {"file": ("article_image.jpg", io.BytesIO(image_data), "image/jpeg")}
        file_response = client.post("/api/v1/files/upload", files=files)
        assert file_response.status_code == 200
        file_id = file_response.json()["file_id"]

        # 4. 記事を下書きで作成
        article_data = {
            "title": "Pythonプログラミング入門",
            "content": "Pythonの基本的な使い方について説明します。",
            "excerpt": "Python入門記事",
            "category_id": category_id,
            "tag_ids": [tag_id],
            "status": "draft",
        }
        article_response = client.post("/api/v1/articles/", json=article_data)
        assert article_response.status_code == 200
        article_id = article_response.json()["id"]
        assert article_response.json()["status"] == "draft"

        # 5. ファイルを記事に関連付け
        associate_response = client.post(
            f"/api/v1/files/{file_id}/associate/article/{article_id}"
        )
        assert associate_response.status_code == 200
        assert associate_response.json()["article_id"] == article_id

        # 6. 記事を公開
        publish_response = client.post(f"/api/v1/articles/{article_id}/publish")
        assert publish_response.status_code == 200
        assert publish_response.json()["status"] == "published"

        # 7. 記事詳細を確認（すべての関連データが含まれることを確認）
        detail_response = client.get(f"/api/v1/articles/{article_id}")
        assert detail_response.status_code == 200
        detail_data = detail_response.json()
        assert detail_data["category_id"] == category_id
        assert len(detail_data["tag_ids"]) == 1
        assert detail_data["tag_ids"][0] == tag_id

    def test_記事検索と絞り込み(self, client: TestClient):
        """記事の検索・フィルタリング機能をテスト."""
        # カテゴリとタグを作成
        tech_category = client.post("/api/v1/categories/", json={"name": "Tech"}).json()
        python_tag = client.post("/api/v1/tags/", json={"name": "Python"}).json()

        # 複数の記事を作成
        articles = [
            {
                "title": "Python基礎",
                "content": "Python入門コンテンツ",
                "category_id": tech_category["id"],
                "tag_ids": [python_tag["id"]],
                "status": "published",
            },
            {
                "title": "JavaScript入門",
                "content": "JavaScript基礎",
                "category_id": tech_category["id"],
                "status": "published",
            },
            {"title": "非公開記事", "content": "下書き記事", "status": "draft"},
        ]

        created_articles = []
        for article_data in articles:
            response = client.post("/api/v1/articles/", json=article_data)
            assert response.status_code == 200
            created_articles.append(response.json())

        # 検索テスト
        search_response = client.get("/api/v1/articles/search?q=Python")
        assert search_response.status_code == 200
        search_results = search_response.json()["articles"]
        assert len(search_results) >= 1
        assert any("Python" in article["title"] for article in search_results)

        # カテゴリ別フィルタ
        category_filter = client.get(
            f"/api/v1/articles/?category_id={tech_category['id']}"
        )
        assert category_filter.status_code == 200
        category_articles = category_filter.json()
        assert len(category_articles) >= 2

        # ステータス別フィルタ（公開記事のみ）
        published_filter = client.get("/api/v1/articles/?status=published")
        assert published_filter.status_code == 200
        published_articles = published_filter.json()
        assert all(article["status"] == "published" for article in published_articles)


class TestPaperWorkflow:
    """論文関連のワークフロー統合テスト."""

    def test_論文管理ワークフロー(self, client: TestClient):
        """論文の追加から評価・分類までのワークフローをテスト."""
        # 1. カテゴリを作成
        category_data = {"name": "Machine Learning", "description": "ML研究論文"}
        category_response = client.post("/api/v1/categories/", json=category_data)
        category_id = category_response.json()["id"]

        # 2. タグを作成
        tags_data = [
            {"name": "Neural Networks"},
            {"name": "Deep Learning"},
            {"name": "Computer Vision"},
        ]
        tag_ids = []
        for tag_data in tags_data:
            tag_response = client.post("/api/v1/tags/", json=tag_data)
            tag_ids.append(tag_response.json()["id"])

        # 3. PDFファイルをアップロード
        pdf_data = b"fake_pdf_content"
        files = {
            "file": ("research_paper.pdf", io.BytesIO(pdf_data), "application/pdf")
        }
        file_response = client.post("/api/v1/files/upload", files=files)
        file_id = file_response.json()["file_id"]

        # 4. 論文を追加
        paper_data = {
            "title": "Deep Learning for Image Recognition",
            "authors": "Smith, J., Johnson, A.",
            "abstract": "最新のディープラーニング手法による画像認識の研究",
            "doi": "10.1000/182",
            "arxiv_id": "2024.12345",
            "published_year": 2024,
            "category_id": category_id,
            "tag_ids": tag_ids,
            "reading_status": "to_read",
        }
        paper_response = client.post("/api/v1/papers/", json=paper_data)
        assert paper_response.status_code == 200
        paper_id = paper_response.json()["id"]

        # 5. ファイルを論文に関連付け
        associate_response = client.post(
            f"/api/v1/files/{file_id}/associate/paper/{paper_id}"
        )
        assert associate_response.status_code == 200

        # 6. 論文を「読了」に更新
        update_response = client.put(
            f"/api/v1/papers/{paper_id}", json={"reading_status": "completed"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["reading_status"] == "completed"

        # 7. 評価を追加
        rating_data = {"rating": 5, "review": "非常に参考になる論文でした"}
        rating_response = client.post(
            f"/api/v1/papers/{paper_id}/rate", json=rating_data
        )
        assert rating_response.status_code == 200
        assert rating_response.json()["rating"] == 5

        # 8. 論文詳細を確認
        detail_response = client.get(f"/api/v1/papers/{paper_id}")
        assert detail_response.status_code == 200
        detail_data = detail_response.json()
        assert detail_data["category_id"] == category_id
        assert len(detail_data["tag_ids"]) == 3
        assert detail_data["rating"] == 5


class TestTagAndCategoryManagement:
    """タグとカテゴリ管理の統合テスト."""

    def test_タグ統合とカテゴリ移動(self, client: TestClient):
        """タグの統合とカテゴリの移動機能をテスト."""
        # 1. 複数のタグを作成
        tag_names = ["機械学習", "ML", "MachineLearning"]
        tag_ids = []
        for name in tag_names:
            response = client.post("/api/v1/tags/", json={"name": name})
            tag_ids.append(response.json()["id"])

        # 2. タグを統合（複数の同義語タグを一つに）
        merge_data = {
            "source_tag_ids": tag_ids[1:],  # ML, MachineLearning
            "target_tag_id": tag_ids[0],  # 機械学習
        }
        merge_response = client.post("/api/v1/tags/merge", json=merge_data)
        assert merge_response.status_code == 200

        # 3. 統合後、元のタグが削除されていることを確認
        for tag_id in tag_ids[1:]:
            response = client.get(f"/api/v1/tags/{tag_id}")
            assert response.status_code == 404

        # 4. 階層カテゴリを作成
        parent_data = {"name": "Technology"}
        parent_response = client.post("/api/v1/categories/", json=parent_data)
        parent_id = parent_response.json()["id"]

        child_data = {"name": "AI", "parent_id": parent_id}
        child_response = client.post("/api/v1/categories/", json=child_data)
        child_id = child_response.json()["id"]

        grandchild_data = {"name": "Machine Learning", "parent_id": child_id}
        grandchild_response = client.post("/api/v1/categories/", json=grandchild_data)
        grandchild_id = grandchild_response.json()["id"]

        # 5. カテゴリを移動（Machine LearningをTechnologyの直下に）
        move_data = {"new_parent_id": parent_id}
        move_response = client.post(
            f"/api/v1/categories/{grandchild_id}/move", json=move_data
        )
        assert move_response.status_code == 200
        assert move_response.json()["parent_id"] == parent_id

        # 6. カテゴリツリーを確認
        tree_response = client.get("/api/v1/categories/tree")
        assert tree_response.status_code == 200


class TestFileManagement:
    """ファイル管理の統合テスト."""

    def test_ファイル関連付けと統計(self, client: TestClient):
        """ファイルの関連付けと統計機能をテスト."""
        # 1. 複数タイプのファイルをアップロード
        files_data = [
            ("image.jpg", b"fake_image", "image/jpeg"),
            ("document.pdf", b"fake_pdf", "application/pdf"),
            ("text.txt", b"fake_text", "text/plain"),
        ]

        file_ids = []
        for filename, content, mime_type in files_data:
            files = {"file": (filename, io.BytesIO(content), mime_type)}
            response = client.post("/api/v1/files/upload", files=files)
            assert response.status_code == 200
            file_ids.append(response.json()["file_id"])

        # 2. 記事と論文を作成
        article_response = client.post(
            "/api/v1/articles/",
            json={"title": "テスト記事", "content": "テストコンテンツ"},
        )
        article_id = article_response.json()["id"]

        paper_response = client.post(
            "/api/v1/papers/", json={"title": "テスト論文", "authors": "Test Author"}
        )
        paper_id = paper_response.json()["id"]

        # 3. ファイルを関連付け
        client.post(f"/api/v1/files/{file_ids[0]}/associate/article/{article_id}")
        client.post(f"/api/v1/files/{file_ids[1]}/associate/paper/{paper_id}")
        # file_ids[2]は孤立ファイルとして残す

        # 4. 孤立ファイルを確認
        orphaned_response = client.get("/api/v1/files/orphaned")
        assert orphaned_response.status_code == 200
        orphaned_files = orphaned_response.json()
        assert len(orphaned_files) >= 1
        assert any(f["id"] == file_ids[2] for f in orphaned_files)

        # 5. ファイル統計を確認
        stats_response = client.get("/api/v1/files/stats")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["total_files"] >= 3
        assert "image" in stats["by_type"]
        assert "pdf" in stats["by_type"] or "document" in stats["by_type"]

        # 6. 一括可視性更新
        visibility_data = {"file_ids": file_ids, "is_public": False}
        visibility_response = client.post(
            "/api/v1/files/bulk/visibility", json=visibility_data
        )
        assert visibility_response.status_code == 200
        updated_files = visibility_response.json()
        assert all(not f["is_public"] for f in updated_files)


class TestDataConsistency:
    """データ整合性とエラーハンドリングのテスト."""

    def test_関連データ削除時の整合性(self, client: TestClient):
        """関連データが削除された時の整合性をテスト."""
        # 1. カテゴリ、タグ、記事を作成
        category_response = client.post(
            "/api/v1/categories/", json={"name": "Test Category"}
        )
        category_id = category_response.json()["id"]

        tag_response = client.post("/api/v1/tags/", json={"name": "Test Tag"})
        tag_id = tag_response.json()["id"]

        article_response = client.post(
            "/api/v1/articles/",
            json={
                "title": "Test Article",
                "content": "Test content",
                "category_id": category_id,
                "tag_ids": [tag_id],
            },
        )
        article_id = article_response.json()["id"]

        # 2. 記事が正しく作成されていることを確認
        article_detail = client.get(f"/api/v1/articles/{article_id}").json()
        assert article_detail["category_id"] == category_id
        assert tag_id in article_detail["tag_ids"]

        # 3. カテゴリに子カテゴリとコンテンツがある状態で削除を試行（失敗するはず）
        delete_response = client.delete(f"/api/v1/categories/{category_id}")
        assert delete_response.status_code == 400  # コンテンツがあるため削除不可

    def test_無効なデータでの作成エラー(self, client: TestClient):
        """無効なデータでの作成がエラーになることをテスト."""
        # 1. 存在しないカテゴリIDで記事作成
        invalid_article = {
            "title": "Invalid Article",
            "content": "Content",
            "category_id": 99999,  # 存在しないID
        }
        response = client.post("/api/v1/articles/", json=invalid_article)
        assert response.status_code == 400

        # 2. 存在しない親カテゴリIDでカテゴリ作成
        invalid_category = {
            "name": "Invalid Category",
            "parent_id": 99999,  # 存在しないID
        }
        response = client.post("/api/v1/categories/", json=invalid_category)
        assert response.status_code == 400

        # 3. 無効な色指定でカテゴリ作成
        invalid_color_category = {
            "name": "Invalid Color Category",
            "color": "invalid-color",  # 無効なHEX色
        }
        response = client.post("/api/v1/categories/", json=invalid_color_category)
        assert response.status_code == 422  # バリデーションエラー


class TestComplexWorkflows:
    """複雑なワークフローの統合テスト."""

    def test_知識ベース構築ワークフロー(self, client: TestClient):
        """完全な知識ベース構築のワークフローをテスト."""
        # 1. カテゴリ階層を構築
        tech_category = client.post(
            "/api/v1/categories/", json={"name": "Technology"}
        ).json()
        ai_category = client.post(
            "/api/v1/categories/",
            json={"name": "Artificial Intelligence", "parent_id": tech_category["id"]},
        ).json()
        ml_category = client.post(
            "/api/v1/categories/",
            json={"name": "Machine Learning", "parent_id": ai_category["id"]},
        ).json()

        # 2. 関連タグを作成
        tags = ["Python", "TensorFlow", "Deep Learning", "Neural Networks"]
        tag_ids = []
        for tag_name in tags:
            response = client.post("/api/v1/tags/", json={"name": tag_name})
            tag_ids.append(response.json()["id"])

        # 3. 研究論文を追加
        papers_data = [
            {
                "title": "Attention Is All You Need",
                "authors": "Vaswani, A., et al.",
                "category_id": ml_category["id"],
                "tag_ids": tag_ids[:2],
                "published_year": 2017,
            },
            {
                "title": "ImageNet Classification with Deep CNNs",
                "authors": "Krizhevsky, A., et al.",
                "category_id": ml_category["id"],
                "tag_ids": tag_ids[2:],
                "published_year": 2012,
            },
        ]

        paper_ids = []
        for paper_data in papers_data:
            response = client.post("/api/v1/papers/", json=paper_data)
            paper_ids.append(response.json()["id"])

        # 4. 解説記事を作成
        articles_data = [
            {
                "title": "Transformer入門",
                "content": "Transformerモデルの基本概念",
                "category_id": ml_category["id"],
                "tag_ids": tag_ids[:3],
                "status": "published",
            },
            {
                "title": "CNN実装ガイド",
                "content": "畳み込みニューラルネットワークの実装",
                "category_id": ml_category["id"],
                "tag_ids": tag_ids[1:],
                "status": "published",
            },
        ]

        article_ids = []
        for article_data in articles_data:
            response = client.post("/api/v1/articles/", json=article_data)
            article_ids.append(response.json()["id"])

        # 5. サポートファイルをアップロード
        files_data = [
            ("transformer_diagram.png", b"diagram_content", "image/png"),
            ("cnn_implementation.py", b"code_content", "text/plain"),
            ("research_notes.pdf", b"notes_content", "application/pdf"),
        ]

        file_ids = []
        for filename, content, mime_type in files_data:
            files = {"file": (filename, io.BytesIO(content), mime_type)}
            response = client.post("/api/v1/files/upload", files=files)
            file_ids.append(response.json()["file_id"])

        # 6. ファイルを記事・論文に関連付け
        client.post(f"/api/v1/files/{file_ids[0]}/associate/article/{article_ids[0]}")
        client.post(f"/api/v1/files/{file_ids[1]}/associate/article/{article_ids[1]}")
        client.post(f"/api/v1/files/{file_ids[2]}/associate/paper/{paper_ids[0]}")

        # 7. 統計情報を確認
        category_stats = client.get("/api/v1/categories/stats").json()
        assert category_stats["total_categories"] >= 3

        tag_stats = client.get("/api/v1/tags/usage-stats").json()
        assert len(tag_stats) >= len(tags)

        file_stats = client.get("/api/v1/files/stats").json()
        assert file_stats["total_files"] >= 3

        # 8. 検索機能を確認
        article_search = client.get("/api/v1/articles/search?q=Transformer").json()
        assert len(article_search["articles"]) >= 1

        paper_search = client.get("/api/v1/papers/search?q=Attention").json()
        assert len(paper_search["papers"]) >= 1

        # 9. カテゴリツリーの確認
        category_tree = client.get("/api/v1/categories/tree").json()
        assert len(category_tree) >= 1

        # 最上位カテゴリが子を持つことを確認
        tech_tree = next(cat for cat in category_tree if cat["name"] == "Technology")
        assert tech_tree["has_children"]
