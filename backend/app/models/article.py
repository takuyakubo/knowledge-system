"""Article model for managing technical articles."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.file import File
    from app.models.tag import Tag

# 記事とタグの多対多関係のための中間テーブル
article_tag_association = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Article(Base, TimestampMixin):
    """技術記事を管理するモデル."""

    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, doc="記事ID")

    # 基本情報
    title: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, doc="記事タイトル"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, doc="記事本文（Markdown形式）"
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True, doc="記事の要約")

    # メタデータ
    slug: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True, doc="URL用スラッグ"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="draft",
        index=True,
        doc="公開ステータス (draft, published, archived)",
    )

    # SEO・表示関連
    meta_description: Mapped[str | None] = mapped_column(
        String(160), nullable=True, doc="メタディスクリプション"
    )
    featured_image_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, doc="アイキャッチ画像URL"
    )

    # 分類
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True, index=True, doc="カテゴリID"
    )

    # 公開設定
    is_public: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, doc="公開フラグ"
    )
    published_at: Mapped[datetime | None] = mapped_column(nullable=True, doc="公開日時")

    # 統計
    view_count: Mapped[int] = mapped_column(default=0, nullable=False, doc="閲覧数")
    like_count: Mapped[int] = mapped_column(default=0, nullable=False, doc="いいね数")

    # リレーション
    category: Mapped["Category | None"] = relationship(
        "Category", back_populates="articles"
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary=article_tag_association, back_populates="articles"
    )
    files: Mapped[list["File"]] = relationship(
        "File", back_populates="article", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """デバッグ用の文字列表現."""
        return f"<Article(id={self.id}, title='{self.title[:30]}...', status='{self.status}')>"

    @property
    def is_published(self) -> bool:
        """記事が公開されているかどうか."""
        return self.status == "published" and self.is_public

    @property
    def word_count(self) -> int:
        """記事の文字数を概算."""
        import re

        # Markdownの記号を除去して文字数をカウント
        text = re.sub(r"[#*`\[\]()_~]", "", self.content)
        return len(text.replace(" ", "").replace("\n", ""))

    def add_tag(self, tag: "Tag") -> None:
        """記事にタグを追加."""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: "Tag") -> None:
        """記事からタグを削除."""
        if tag in self.tags:
            self.tags.remove(tag)

    def increment_view_count(self) -> None:
        """閲覧数をインクリメント."""
        self.view_count += 1

    def increment_like_count(self) -> None:
        """いいね数をインクリメント."""
        self.like_count += 1
