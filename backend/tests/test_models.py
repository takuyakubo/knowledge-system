"""Tests for database models."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


import pytest
from app.models import Article, Category, File, Paper, Tag


def test_正常系_Articleモデルの基本操作():
    """Articleモデルの基本的な操作をテスト."""
    article = Article(
        title="Test Article",
        content="# Test Content\n\nThis is a test article.",
        status="published",
        is_public=True,
    )

    assert article.title == "Test Article"
    assert article.status == "published"
    assert article.is_published is True
    assert article.word_count > 0
    assert "Test Article" in repr(article)


def test_正常系_Paperモデルの基本操作():
    """Paperモデルの基本的な操作をテスト."""
    paper = Paper(
        title="Machine Learning in Practice",
        authors="John Doe, Jane Smith",
        publication_year=2023,
        doi="10.1000/test.2023.001",
        rating=4,
    )

    assert paper.title == "Machine Learning in Practice"
    assert paper.first_author == "John Doe"
    assert len(paper.author_list) == 2
    assert paper.rating == 4
    assert "Machine Learning" in repr(paper)


def test_正常系_Paperモデルの引用テキスト生成():
    """Paperモデルの引用テキスト生成をテスト."""
    paper = Paper(
        title="Deep Learning Fundamentals",
        authors="Alice Johnson",
        journal="AI Journal",
        publication_year=2022,
        doi="10.1000/ai.2022.001",
    )

    citation = paper.citation_text
    assert "Alice Johnson" in citation
    assert "Deep Learning Fundamentals" in citation
    assert "AI Journal" in citation
    assert "(2022)" in citation
    assert "DOI: 10.1000/ai.2022.001" in citation


def test_正常系_Fileモデルの基本操作():
    """Fileモデルの基本的な操作をテスト."""
    file = File(
        filename="test.pdf",
        original_filename="Original Test.pdf",
        file_path="/uploads/test.pdf",
        file_size=1024 * 1024,  # 1MB
        mime_type="application/pdf",
        file_extension="pdf",
        file_type="pdf",
    )

    assert file.filename == "test.pdf"
    assert file.file_size_mb == 1.0
    assert file.file_size_readable == "1.0 MB"
    assert file.is_pdf is True
    assert file.is_image is False
    assert file.is_document is True


def test_正常系_Fileモデルの各種判定メソッド():
    """Fileモデルの種別判定メソッドをテスト."""
    # 画像ファイル
    image_file = File(
        filename="image.jpg",
        original_filename="image.jpg",
        file_path="/uploads/image.jpg",
        file_size=500000,
        mime_type="image/jpeg",
        file_extension="jpg",
        file_type="image",
    )
    assert image_file.is_image is True
    assert image_file.is_pdf is False

    # PDFファイル
    pdf_file = File(
        filename="doc.pdf",
        original_filename="doc.pdf",
        file_path="/uploads/doc.pdf",
        file_size=1000000,
        mime_type="application/pdf",
        file_extension="pdf",
        file_type="pdf",
    )
    assert pdf_file.is_pdf is True
    assert pdf_file.is_document is True


def test_正常系_Tagモデルの基本操作():
    """Tagモデルの基本的な操作をテスト."""
    tag = Tag(
        name="Python",
        slug="python",
        description="Programming language",
        color="#3776ab",
        usage_count=0,  # デフォルト値を明示的に設定
    )

    assert tag.name == "Python"
    assert tag.slug == "python"
    assert tag.usage_count == 0

    # 使用回数の操作
    tag.increment_usage_count()
    assert tag.usage_count == 1

    tag.decrement_usage_count()
    assert tag.usage_count == 0

    # 0以下にはならない
    tag.decrement_usage_count()
    assert tag.usage_count == 0


def test_正常系_Tagモデルのスラッグ生成():
    """Tagモデルのスラッグ生成をテスト."""
    slug = Tag.create_slug_from_name("Machine Learning")
    assert slug == "machine-learning"

    slug = Tag.create_slug_from_name("Python 3.12")
    assert slug == "python-3-12"

    slug = Tag.create_slug_from_name("Web Development")
    assert slug == "web-development"


def test_正常系_Categoryモデルの基本操作():
    """Categoryモデルの基本的な操作をテスト."""
    # 親カテゴリ
    parent = Category(
        name="Technology", slug="technology", description="Technology related content"
    )
    parent.update_path()

    assert parent.name == "Technology"
    assert parent.is_root is True
    assert parent.path == "/technology"
    assert parent.level == 0

    # 子カテゴリ
    child = Category(name="Programming", slug="programming", parent=parent)
    child.update_path()

    assert child.is_root is False
    assert child.level == 1
    assert child.path == "/technology/programming"
    assert child.full_name == "Technology > Programming"


def test_正常系_Categoryモデルの階層操作():
    """Categoryモデルの階層操作をテスト."""
    # ルートカテゴリ
    tech = Category(name="Technology", slug="tech")
    tech.update_path()

    # 子カテゴリ
    programming = Category(name="Programming", slug="programming", parent=tech)
    programming.update_path()

    # 孫カテゴリ
    python = Category(name="Python", slug="python", parent=programming)
    python.update_path()

    # パンくずリストの確認
    breadcrumbs = python.breadcrumbs
    assert len(breadcrumbs) == 3
    assert breadcrumbs[0].name == "Technology"
    assert breadcrumbs[1].name == "Programming"
    assert breadcrumbs[2].name == "Python"


def test_正常系_Categoryモデルのスラッグ生成():
    """Categoryモデルのスラッグ生成をテスト."""
    slug = Category.create_slug_from_name("Web Development")
    assert slug == "web-development"

    slug = Category.create_slug_from_name("Data Science & AI")
    assert slug == "data-science-ai"


def test_異常系_Paperモデルの評価設定():
    """Paperモデルの評価設定で異常値をテスト."""
    paper = Paper(title="Test Paper", authors="Test Author")

    # 正常範囲
    paper.set_rating(3)
    assert paper.rating == 3

    # 異常値でエラー
    with pytest.raises(ValueError):
        paper.set_rating(0)

    with pytest.raises(ValueError):
        paper.set_rating(6)


def test_正常系_Paperモデルの状態変更():
    """Paperモデルの読書状態変更をテスト."""
    paper = Paper(
        title="Test Paper",
        authors="Test Author",
        reading_status="to_read",  # デフォルト値を明示的に設定
    )

    assert paper.reading_status == "to_read"
    assert paper.read_at is None

    paper.mark_as_read()
    assert paper.reading_status == "completed"
    assert paper.read_at is not None


def test_正常系_Paperモデルのお気に入り切り替え():
    """Paperモデルのお気に入り機能をテスト."""
    paper = Paper(
        title="Test Paper",
        authors="Test Author",
        is_favorite=False,  # デフォルト値を明示的に設定
    )

    assert paper.is_favorite is False

    paper.toggle_favorite()
    assert paper.is_favorite is True

    paper.toggle_favorite()
    assert paper.is_favorite is False


def test_正常系_Fileモデルのクラスメソッド():
    """Fileモデルのクラスメソッドをテスト."""
    # ファイル種別の判定
    assert File.get_file_type_from_mime("image/jpeg") == "image"
    assert File.get_file_type_from_mime("application/pdf") == "pdf"
    assert File.get_file_type_from_mime("video/mp4") == "video"
    assert File.get_file_type_from_mime("audio/mpeg") == "audio"
    assert File.get_file_type_from_mime("text/plain") == "document"
    assert File.get_file_type_from_mime("application/octet-stream") == "other"

    # 拡張子の取得
    assert File.get_extension_from_filename("test.pdf") == "pdf"
    assert File.get_extension_from_filename("image.JPG") == "jpg"
    assert File.get_extension_from_filename("document.docx") == "docx"
