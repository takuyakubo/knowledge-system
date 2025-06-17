"""Category model for hierarchical organization of content."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.paper import Paper


class Category(Base, TimestampMixin):
    """階層的なカテゴリを管理するモデル."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, doc="カテゴリID")

    # 基本情報
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, doc="カテゴリ名"
    )
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True, doc="URL用スラッグ"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, doc="カテゴリの説明"
    )

    # 階層構造
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True, index=True, doc="親カテゴリID"
    )
    level: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, doc="階層レベル(0が最上位)"
    )
    path: Mapped[str] = mapped_column(
        String(500), nullable=False, index=True, doc="階層パス(例: /tech/ai/ml)"
    )

    # 表示設定
    color: Mapped[str | None] = mapped_column(
        String(7), nullable=True, doc="カテゴリの色(HEXカラーコード)"
    )
    icon: Mapped[str | None] = mapped_column(
        String(50), nullable=True, doc="アイコン名"
    )

    # メタデータ
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, doc="有効フラグ"
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, doc="システムカテゴリフラグ"
    )

    # 順序・表示
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, doc="同階層内での表示順序"
    )

    # 統計
    article_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, doc="記事数"
    )
    paper_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, doc="論文数"
    )

    # SEO
    meta_title: Mapped[str | None] = mapped_column(
        String(60), nullable=True, doc="SEO用タイトル"
    )
    meta_description: Mapped[str | None] = mapped_column(
        String(160), nullable=True, doc="SEO用メタディスクリプション"
    )

    # リレーション
    parent: Mapped["Category | None"] = relationship(
        "Category", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["Category"]] = relationship(
        "Category", back_populates="parent", cascade="all, delete-orphan"
    )
    articles: Mapped[list["Article"]] = relationship(
        "Article", back_populates="category"
    )
    papers: Mapped[list["Paper"]] = relationship("Paper", back_populates="category")

    def __repr__(self) -> str:
        """デバッグ用の文字列表現."""
        return f"<Category(id={self.id}, name='{self.name}', level={self.level})>"

    @property
    def full_name(self) -> str:
        """階層を含む完全な名前を取得."""
        if self.parent:
            return f"{self.parent.full_name} > {self.name}"
        return self.name

    @property
    def total_content_count(self) -> int:
        """記事と論文の総数."""
        return self.article_count + self.paper_count

    @property
    def has_children(self) -> bool:
        """子カテゴリを持つかどうか."""
        return len(self.children) > 0

    @property
    def is_root(self) -> bool:
        """ルートカテゴリかどうか."""
        return self.parent is None

    @property
    def breadcrumbs(self) -> list["Category"]:
        """パンくずリスト用の親カテゴリリストを取得."""
        breadcrumbs = []
        current = self

        while current:
            breadcrumbs.insert(0, current)
            current = current.parent

        return breadcrumbs

    def get_all_children(self, recursive: bool = True) -> list["Category"]:
        """すべての子カテゴリを取得（再帰的に）."""
        all_children = list(self.children)

        if recursive:
            for child in self.children:
                all_children.extend(child.get_all_children(recursive=True))

        return all_children

    def get_all_descendants_ids(self) -> list[int]:
        """すべての子孫カテゴリのIDを取得."""
        descendants = []
        for child in self.children:
            descendants.append(child.id)
            descendants.extend(child.get_all_descendants_ids())
        return descendants

    def update_path(self) -> None:
        """階層パスを更新."""
        if self.parent:
            self.path = f"{self.parent.path}/{self.slug}"
            self.level = self.parent.level + 1
        else:
            self.path = f"/{self.slug}"
            self.level = 0

    def update_counts(self) -> None:
        """記事数・論文数を再計算."""
        # 直接の記事数・論文数をカウント
        self.article_count = len([a for a in self.articles if a.is_published])
        self.paper_count = len(self.papers)

        # 子カテゴリの数も含める場合は以下のようにする
        # for child in self.children:
        #     child.update_counts()
        #     self.article_count += child.article_count
        #     self.paper_count += child.paper_count

    def move_to_parent(self, new_parent: "Category | None") -> None:
        """カテゴリを別の親の下に移動."""
        self.parent = new_parent
        self.parent_id = new_parent.id if new_parent else None
        self.update_path()

        # 子カテゴリのパスも更新
        for child in self.children:
            child.update_path()

    @classmethod
    def create_slug_from_name(cls, name: str) -> str:
        """カテゴリ名からスラッグを生成."""
        import re
        import unicodedata

        # Unicode正規化
        slug = unicodedata.normalize("NFKD", name)

        # ASCII文字以外を削除し、小文字に変換
        slug = re.sub(r"[^\w\s-]", "", slug).strip().lower()

        # スペースとアンダースコアをハイフンに変換
        slug = re.sub(r"[\s_]+", "-", slug)

        # 連続するハイフンを単一のハイフンに変換
        slug = re.sub(r"-+", "-", slug)

        # 先頭と末尾のハイフンを削除
        slug = slug.strip("-")

        return slug or "category"  # 空の場合はデフォルト値

    @classmethod
    def get_root_categories(cls, session) -> list["Category"]:
        """ルートカテゴリ（親を持たないカテゴリ）を取得."""
        return (
            session.query(cls)
            .filter(cls.parent_id.is_(None))
            .filter(cls.is_active)
            .order_by(cls.sort_order, cls.name)
            .all()
        )

    @classmethod
    def get_category_tree(cls, session) -> dict:
        """階層的なカテゴリツリーを取得."""

        def build_tree(categories: list["Category"]) -> dict:
            tree = {}
            for category in categories:
                tree[category.id] = {
                    "category": category,
                    "children": build_tree(category.children),
                }
            return tree

        root_categories = cls.get_root_categories(session)
        return build_tree(root_categories)
