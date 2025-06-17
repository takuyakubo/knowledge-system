"""Article schemas for API serialization."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ArticleBase(BaseModel):
    """Base article schema."""

    title: str = Field(..., max_length=255, description="記事タイトル")
    content: str = Field(..., description="記事本文(Markdown形式)")
    summary: str | None = Field(None, description="記事の要約")
    slug: str | None = Field(None, max_length=255, description="URL用スラッグ")
    status: str = Field(default="draft", description="公開ステータス")
    meta_description: str | None = Field(
        None, max_length=160, description="SEO用メタディスクリプション"
    )
    featured_image_url: str | None = Field(
        None, max_length=500, description="アイキャッチ画像URL"
    )
    is_public: bool = Field(default=False, description="公開フラグ")


class ArticleCreate(ArticleBase):
    """Article creation schema."""

    category_id: int | None = Field(None, description="カテゴリID")


class ArticleUpdate(BaseModel):
    """Article update schema."""

    title: str | None = Field(None, max_length=255, description="記事タイトル")
    content: str | None = Field(None, description="記事本文(Markdown形式)")
    summary: str | None = Field(None, description="記事の要約")
    slug: str | None = Field(None, max_length=255, description="URL用スラッグ")
    status: str | None = Field(None, description="公開ステータス")
    meta_description: str | None = Field(
        None, max_length=160, description="SEO用メタディスクリプション"
    )
    featured_image_url: str | None = Field(
        None, max_length=500, description="アイキャッチ画像URL"
    )
    is_public: bool | None = Field(None, description="公開フラグ")
    category_id: int | None = Field(None, description="カテゴリID")


class ArticleInDBBase(ArticleBase):
    """Base article schema with database fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int | None = None
    published_at: datetime | None = None
    view_count: int = 0
    like_count: int = 0
    created_at: datetime
    updated_at: datetime


class Article(ArticleInDBBase):
    """Article schema for API responses."""

    pass


class ArticleInDB(ArticleInDBBase):
    """Article schema for database storage."""

    pass


class ArticleList(BaseModel):
    """Article list response schema."""

    items: list[Article]
    total: int
    page: int
    size: int
    pages: int


class ArticlePublish(BaseModel):
    """Article publish/unpublish schema."""

    is_public: bool = Field(..., description="公開フラグ")
