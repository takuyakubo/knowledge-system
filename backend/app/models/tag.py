"""Tag model for organizing and categorizing content."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.paper import Paper


class Tag(Base, TimestampMixin):
    """タグを管理するモデル."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, doc="タグID")

    # 基本情報
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True, doc="タグ名"
    )
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True, doc="URL用スラッグ"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, doc="タグの説明"
    )

    # 表示設定
    color: Mapped[str | None] = mapped_column(
        String(7), nullable=True, doc="タグの色（HEXカラーコード）"
    )
    icon: Mapped[str | None] = mapped_column(
        String(50), nullable=True, doc="アイコン名"
    )

    # メタデータ
    is_system: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, doc="システムタグフラグ"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, doc="有効フラグ"
    )

    # 統計
    usage_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, server_default=text("0"), doc="使用回数"
    )

    # 順序・重要度
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, doc="表示順序"
    )

    # リレーション
    articles: Mapped[list["Article"]] = relationship(
        "Article", secondary="article_tags", back_populates="tags"
    )
    papers: Mapped[list["Paper"]] = relationship(
        "Paper", secondary="paper_tags", back_populates="tags"
    )

    def __repr__(self) -> str:
        """デバッグ用の文字列表現."""
        return (
            f"<Tag(id={self.id}, name='{self.name}', usage_count={self.usage_count})>"
        )

    @property
    def total_usage_count(self) -> int:
        """記事と論文での総使用回数."""
        return len(self.articles) + len(self.papers)

    def increment_usage_count(self) -> None:
        """使用回数をインクリメント."""
        self.usage_count += 1

    def decrement_usage_count(self) -> None:
        """使用回数をデクリメント（0以下にはならない）."""
        if self.usage_count > 0:
            self.usage_count -= 1

    def update_usage_count(self) -> None:
        """実際の使用回数を再計算して更新."""
        self.usage_count = self.total_usage_count

    @classmethod
    def create_slug_from_name(cls, name: str) -> str:
        """タグ名からスラッグを生成."""
        import re
        import unicodedata

        # Unicode正規化
        slug = unicodedata.normalize("NFKD", name)

        # ASCII文字以外を削除し、小文字に変換
        slug = re.sub(r"[^\w\s.-]", "", slug).strip().lower()

        # ピリオドをハイフンに変換（3.12 -> 3-12）
        slug = re.sub(r"\.", "-", slug)

        # スペースとアンダースコアをハイフンに変換
        slug = re.sub(r"[\s_]+", "-", slug)

        # 連続するハイフンを単一のハイフンに変換
        slug = re.sub(r"-+", "-", slug)

        # 先頭と末尾のハイフンを削除
        slug = slug.strip("-")

        return slug or "tag"  # 空の場合はデフォルト値

    @classmethod
    def get_or_create_tags(cls, session, tag_names: list[str]) -> list["Tag"]:
        """タグ名のリストから既存タグを取得、または新規作成."""
        tags = []

        for name in tag_names:
            name = name.strip()
            if not name:
                continue

            # 既存タグを検索
            tag = session.query(cls).filter(cls.name == name).first()

            if not tag:
                # 新規作成
                slug = cls.create_slug_from_name(name)

                # スラッグの重複を避ける
                base_slug = slug
                counter = 1
                while session.query(cls).filter(cls.slug == slug).first():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                tag = cls(name=name, slug=slug)
                session.add(tag)

            tags.append(tag)

        return tags

    def get_related_tags(self, limit: int = 10) -> list["Tag"]:
        """関連するタグを取得（共起頻度ベース）."""
        from sqlalchemy import and_, func

        from app.models.article import article_tag_association

        # 記事での共起タグ
        article_cooccur = (
            self.__class__.query.join(
                article_tag_association,
                article_tag_association.c.tag_id == self.__class__.id,
            )
            .join(
                article_tag_association.alias("aa2"),
                and_(
                    article_tag_association.c.article_id
                    == article_tag_association.alias("aa2").c.article_id,
                    article_tag_association.alias("aa2").c.tag_id != self.id,
                ),
            )
            .filter(article_tag_association.alias("aa2").c.tag_id == self.__class__.id)
            .group_by(self.__class__.id)
            .order_by(func.count().desc())
            .limit(limit)
        )

        # 実際の実装では、より効率的なクエリが必要
        # ここでは簡略化した形で示す
        return []
