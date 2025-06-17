"""Category schemas for API endpoints."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class CategoryBase(BaseModel):
    """Category base schema."""

    name: str = Field(..., max_length=100, description="カテゴリ名")
    slug: str | None = Field(None, max_length=100, description="URL用スラッグ")
    description: str | None = Field(None, description="カテゴリの説明")
    parent_id: int | None = Field(None, description="親カテゴリID")
    color: str | None = Field(
        None, max_length=7, description="カテゴリの色(HEXカラーコード)"
    )
    icon: str | None = Field(None, max_length=50, description="アイコン名")
    is_active: bool = Field(default=True, description="有効フラグ")
    is_system: bool = Field(default=False, description="システムカテゴリフラグ")
    sort_order: int = Field(default=0, description="同階層内での表示順序")
    meta_title: str | None = Field(None, max_length=60, description="SEO用タイトル")
    meta_description: str | None = Field(
        None, max_length=160, description="SEO用メタディスクリプション"
    )

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str | None) -> str | None:
        """HEXカラーコードの検証."""
        if v is None:
            return v
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("色は#から始まる7文字のHEXカラーコードで指定してください")
        try:
            int(v[1:], 16)
        except ValueError as e:
            raise ValueError("有効なHEXカラーコードを指定してください") from e
        return v


class CategoryCreate(CategoryBase):
    """Category creation schema."""

    pass


class CategoryUpdate(BaseModel):
    """Category update schema."""

    name: str | None = Field(None, max_length=100, description="カテゴリ名")
    slug: str | None = Field(None, max_length=100, description="URL用スラッグ")
    description: str | None = Field(None, description="カテゴリの説明")
    parent_id: int | None = Field(None, description="親カテゴリID")
    color: str | None = Field(None, max_length=7, description="カテゴリの色")
    icon: str | None = Field(None, max_length=50, description="アイコン名")
    is_active: bool | None = Field(None, description="有効フラグ")
    is_system: bool | None = Field(None, description="システムカテゴリフラグ")
    sort_order: int | None = Field(None, description="表示順序")
    meta_title: str | None = Field(None, max_length=60, description="SEO用タイトル")
    meta_description: str | None = Field(
        None, max_length=160, description="SEO用メタディスクリプション"
    )

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str | None) -> str | None:
        """HEXカラーコードの検証."""
        if v is None:
            return v
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("色は#から始まる7文字のHEXカラーコードで指定してください")
        try:
            int(v[1:], 16)
        except ValueError as e:
            raise ValueError("有効なHEXカラーコードを指定してください") from e
        return v


class CategoryMove(BaseModel):
    """Category move schema."""

    new_parent_id: int | None = Field(None, description="新しい親カテゴリID")


class CategoryBulkUpdate(BaseModel):
    """Category bulk update schema."""

    category_ids: list[int] = Field(..., description="更新するカテゴリIDリスト")
    updates: CategoryUpdate = Field(..., description="更新内容")


class CategoryTree(BaseModel):
    """Hierarchical category tree schema."""

    id: int = Field(..., description="カテゴリID")
    name: str = Field(..., description="カテゴリ名")
    slug: str = Field(..., description="スラッグ")
    description: str | None = Field(None, description="説明")
    level: int = Field(..., description="階層レベル")
    path: str = Field(..., description="階層パス")
    color: str | None = Field(None, description="カテゴリ色")
    icon: str | None = Field(None, description="アイコン")
    is_active: bool = Field(..., description="有効フラグ")
    article_count: int = Field(..., description="記事数")
    paper_count: int = Field(..., description="論文数")
    total_content_count: int = Field(..., description="総コンテンツ数")
    has_children: bool = Field(..., description="子カテゴリを持つか")
    children: list["CategoryTree"] = Field(default=[], description="子カテゴリ")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class CategoryBreadcrumb(BaseModel):
    """Category breadcrumb schema."""

    id: int = Field(..., description="カテゴリID")
    name: str = Field(..., description="カテゴリ名")
    slug: str = Field(..., description="スラッグ")
    path: str = Field(..., description="パス")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class Category(CategoryBase):
    """Category response schema."""

    id: int = Field(..., description="カテゴリID")
    level: int = Field(..., description="階層レベル")
    path: str = Field(..., description="階層パス")
    article_count: int = Field(..., description="記事数")
    paper_count: int = Field(..., description="論文数")
    total_content_count: int = Field(..., description="総コンテンツ数")
    has_children: bool = Field(..., description="子カテゴリを持つか")
    is_root: bool = Field(..., description="ルートカテゴリか")
    full_name: str = Field(..., description="階層を含む完全な名前")
    breadcrumbs: list[CategoryBreadcrumb] = Field(
        default=[], description="パンくずリスト"
    )
    children: list["Category"] = Field(default=[], description="子カテゴリ")
    created_at: str = Field(..., description="作成日時")
    updated_at: str = Field(..., description="更新日時")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class CategoryStats(BaseModel):
    """Category statistics schema."""

    total_categories: int = Field(..., description="総カテゴリ数")
    active_categories: int = Field(..., description="有効カテゴリ数")
    root_categories: int = Field(..., description="ルートカテゴリ数")
    max_depth: int = Field(..., description="最大階層深度")
    categories_by_level: dict[int, int] = Field(..., description="階層別カテゴリ数")
    top_categories: list[dict[str, Any]] = Field(..., description="人気カテゴリ")


class CategorySearchResult(BaseModel):
    """Category search result schema."""

    categories: list[Category] = Field(..., description="カテゴリリスト")
    total: int = Field(..., description="総件数")
    page: int = Field(..., description="ページ番号")
    size: int = Field(..., description="ページサイズ")
    has_next: bool = Field(..., description="次のページがあるか")
