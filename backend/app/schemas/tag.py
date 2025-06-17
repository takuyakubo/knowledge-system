"""Tag schemas for API serialization."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TagBase(BaseModel):
    """Base tag schema."""

    name: str = Field(..., max_length=100, description="タグ名")
    slug: str | None = Field(None, max_length=100, description="URL用スラッグ")
    description: str | None = Field(None, description="タグの説明")
    color: str | None = Field(
        None, max_length=7, description="タグの色(HEXカラーコード)"
    )
    icon: str | None = Field(None, max_length=50, description="アイコン名")
    is_system: bool = Field(default=False, description="システムタグフラグ")
    is_active: bool = Field(default=True, description="有効フラグ")
    sort_order: int = Field(default=0, description="表示順序")


class TagCreate(TagBase):
    """Tag creation schema."""

    pass


class TagUpdate(BaseModel):
    """Tag update schema."""

    name: str | None = Field(None, max_length=100, description="タグ名")
    slug: str | None = Field(None, max_length=100, description="URL用スラッグ")
    description: str | None = Field(None, description="タグの説明")
    color: str | None = Field(
        None, max_length=7, description="タグの色(HEXカラーコード)"
    )
    icon: str | None = Field(None, max_length=50, description="アイコン名")
    is_system: bool | None = Field(None, description="システムタグフラグ")
    is_active: bool | None = Field(None, description="有効フラグ")
    sort_order: int | None = Field(None, description="表示順序")


class TagInDBBase(TagBase):
    """Base tag schema with database fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime


class Tag(TagInDBBase):
    """Tag schema for API responses."""

    pass


class TagInDB(TagInDBBase):
    """Tag schema for database storage."""

    pass


class TagList(BaseModel):
    """Tag list response schema."""

    items: list[Tag]
    total: int
    page: int
    size: int
    pages: int


class TagUsageStats(BaseModel):
    """Tag usage statistics schema."""

    tag_id: int
    tag_name: str
    usage_count: int
    article_count: int
    paper_count: int


class TagBulkCreate(BaseModel):
    """Bulk tag creation schema."""

    tag_names: list[str] = Field(..., description="作成するタグ名のリスト")


class TagMerge(BaseModel):
    """Tag merge schema."""

    source_tag_ids: list[int] = Field(..., description="統合元のタグIDリスト")
    target_tag_id: int = Field(..., description="統合先のタグID")
