"""Paper model for managing research papers."""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.file import File
    from app.models.tag import Tag

# 論文とタグの多対多関係のための中間テーブル
paper_tag_association = Table(
    "paper_tags",
    Base.metadata,
    Column("paper_id", ForeignKey("papers.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Paper(Base, TimestampMixin):
    """研究論文を管理するモデル."""

    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(primary_key=True, doc="論文ID")

    # 基本情報
    title: Mapped[str] = mapped_column(
        String(500), nullable=False, index=True, doc="論文タイトル"
    )
    abstract: Mapped[str | None] = mapped_column(
        Text, nullable=True, doc="論文の要約(Abstract)"
    )

    # 著者・出版情報
    authors: Mapped[str] = mapped_column(
        Text, nullable=False, doc="著者名(カンマ区切り)"
    )
    journal: Mapped[str | None] = mapped_column(
        String(255), nullable=True, doc="ジャーナル名"
    )
    conference: Mapped[str | None] = mapped_column(
        String(255), nullable=True, doc="学会名"
    )
    publisher: Mapped[str | None] = mapped_column(
        String(255), nullable=True, doc="出版社"
    )

    # 発行情報
    publication_year: Mapped[int | None] = mapped_column(
        Integer, nullable=True, index=True, doc="発行年"
    )
    publication_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, doc="発行日"
    )
    volume: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="巻号")
    issue: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="号数")
    pages: Mapped[str | None] = mapped_column(
        String(50), nullable=True, doc="ページ範囲"
    )

    # 識別子
    doi: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True, index=True, doc="DOI"
    )
    arxiv_id: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True, index=True, doc="arXiv ID"
    )
    pmid: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True, index=True, doc="PubMed ID"
    )
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True, doc="ISBN")

    # URL・参照
    url: Mapped[str | None] = mapped_column(String(500), nullable=True, doc="論文URL")
    pdf_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, doc="PDF URL"
    )

    # メタデータ
    language: Mapped[str] = mapped_column(
        String(10), default="en", nullable=False, doc="言語コード"
    )
    paper_type: Mapped[str] = mapped_column(
        String(50),
        default="journal",
        nullable=False,
        doc="論文種別 (journal, conference, preprint, thesis, book)",
    )

    # 個人的なメモ・評価
    personal_notes: Mapped[str | None] = mapped_column(
        Text, nullable=True, doc="個人的なメモ"
    )
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True, doc="評価(1-5)")
    reading_status: Mapped[str] = mapped_column(
        String(20),
        default="to_read",
        nullable=False,
        server_default=text("'to_read'"),
        doc="読書ステータス (to_read, reading, completed, skipped)",
    )

    # 重要度・優先度
    priority: Mapped[int] = mapped_column(
        Integer, default=3, nullable=False, doc="優先度(1-5、5が最高)"
    )
    is_favorite: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default=text("0"),
        doc="お気に入りフラグ",
    )

    # 分類
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True, index=True, doc="カテゴリID"
    )

    # 統計
    citation_count: Mapped[int] = mapped_column(
        default=0, nullable=False, doc="被引用数"
    )

    # 読書記録
    read_at: Mapped[datetime | None] = mapped_column(nullable=True, doc="読了日時")

    # リレーション
    category: Mapped["Category | None"] = relationship(
        "Category", back_populates="papers"
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary=paper_tag_association, back_populates="papers"
    )
    files: Mapped[list["File"]] = relationship(
        "File", back_populates="paper", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """デバッグ用の文字列表現."""
        return (
            f"<Paper(id={self.id}, title='{self.title[:50]}...', "
            f"year={self.publication_year})>"
        )

    @property
    def author_list(self) -> list[str]:
        """著者名をリストとして取得."""
        return (
            [author.strip() for author in self.authors.split(",")]
            if self.authors
            else []
        )

    @property
    def first_author(self) -> str | None:
        """筆頭著者を取得."""
        authors = self.author_list
        return authors[0] if authors else None

    @property
    def citation_text(self) -> str:
        """引用形式のテキストを生成."""
        citation_parts = []

        # 著者
        if self.authors:
            citation_parts.append(self.authors)

        # タイトル
        citation_parts.append(f'"{self.title}"')

        # ジャーナル・学会
        if self.journal:
            citation_parts.append(self.journal)
        elif self.conference:
            citation_parts.append(self.conference)

        # 年
        if self.publication_year:
            citation_parts.append(f"({self.publication_year})")

        # DOI
        if self.doi:
            citation_parts.append(f"DOI: {self.doi}")

        return ", ".join(citation_parts)

    def add_tag(self, tag: "Tag") -> None:
        """論文にタグを追加."""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: "Tag") -> None:
        """論文からタグを削除."""
        if tag in self.tags:
            self.tags.remove(tag)

    def mark_as_read(self) -> None:
        """論文を読了としてマーク."""
        self.reading_status = "completed"
        self.read_at = datetime.now()

    def set_rating(self, rating: int) -> None:
        """評価を設定（1-5の範囲チェック付き）."""
        if 1 <= rating <= 5:
            self.rating = rating
        else:
            raise ValueError("Rating must be between 1 and 5")

    def toggle_favorite(self) -> None:
        """お気に入りの状態を切り替え."""
        self.is_favorite = not self.is_favorite
