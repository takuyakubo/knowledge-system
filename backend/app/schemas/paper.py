"""Paper schemas for API serialization."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PaperBase(BaseModel):
    """Base paper schema."""

    title: str = Field(..., max_length=500, description="論文タイトル")
    abstract: str | None = Field(None, description="論文の要約(Abstract)")
    authors: str = Field(..., description="著者名(カンマ区切り)")
    journal: str | None = Field(None, max_length=255, description="ジャーナル名")
    conference: str | None = Field(None, max_length=255, description="学会名")
    publisher: str | None = Field(None, max_length=255, description="出版社")
    publication_year: int | None = Field(None, description="発行年")
    publication_date: date | None = Field(None, description="発行日")
    volume: str | None = Field(None, max_length=50, description="巻号")
    issue: str | None = Field(None, max_length=50, description="号数")
    pages: str | None = Field(None, max_length=50, description="ページ範囲")
    doi: str | None = Field(None, max_length=100, description="DOI")
    arxiv_id: str | None = Field(None, max_length=50, description="arXiv ID")
    pmid: str | None = Field(None, max_length=20, description="PubMed ID")
    isbn: str | None = Field(None, max_length=20, description="ISBN")
    url: str | None = Field(None, max_length=500, description="論文URL")
    pdf_url: str | None = Field(None, max_length=500, description="PDF URL")
    language: str = Field(default="en", max_length=10, description="言語コード")
    paper_type: str = Field(
        default="journal",
        max_length=50,
        description="論文種別 (journal, conference, preprint, thesis, book)",
    )
    personal_notes: str | None = Field(None, description="個人的なメモ")
    rating: int | None = Field(None, ge=1, le=5, description="評価(1-5)")
    reading_status: str = Field(
        default="to_read",
        max_length=20,
        description="読書ステータス (to_read, reading, completed, skipped)",
    )
    priority: int = Field(default=3, ge=1, le=5, description="優先度(1-5、5が最高)")
    is_favorite: bool = Field(default=False, description="お気に入りフラグ")
    citation_count: int = Field(default=0, ge=0, description="被引用数")


class PaperCreate(PaperBase):
    """Paper creation schema."""

    category_id: int | None = Field(None, description="カテゴリID")
    tag_ids: list[int] = Field(default_factory=list, description="タグIDのリスト")


class PaperUpdate(BaseModel):
    """Paper update schema."""

    title: str | None = Field(None, max_length=500, description="論文タイトル")
    abstract: str | None = Field(None, description="論文の要約(Abstract)")
    authors: str | None = Field(None, description="著者名(カンマ区切り)")
    journal: str | None = Field(None, max_length=255, description="ジャーナル名")
    conference: str | None = Field(None, max_length=255, description="学会名")
    publisher: str | None = Field(None, max_length=255, description="出版社")
    publication_year: int | None = Field(None, description="発行年")
    publication_date: date | None = Field(None, description="発行日")
    volume: str | None = Field(None, max_length=50, description="巻号")
    issue: str | None = Field(None, max_length=50, description="号数")
    pages: str | None = Field(None, max_length=50, description="ページ範囲")
    doi: str | None = Field(None, max_length=100, description="DOI")
    arxiv_id: str | None = Field(None, max_length=50, description="arXiv ID")
    pmid: str | None = Field(None, max_length=20, description="PubMed ID")
    isbn: str | None = Field(None, max_length=20, description="ISBN")
    url: str | None = Field(None, max_length=500, description="論文URL")
    pdf_url: str | None = Field(None, max_length=500, description="PDF URL")
    language: str | None = Field(None, max_length=10, description="言語コード")
    paper_type: str | None = Field(None, max_length=50, description="論文種別")
    personal_notes: str | None = Field(None, description="個人的なメモ")
    rating: int | None = Field(None, ge=1, le=5, description="評価(1-5)")
    reading_status: str | None = Field(
        None, max_length=20, description="読書ステータス"
    )
    priority: int | None = Field(None, ge=1, le=5, description="優先度")
    is_favorite: bool | None = Field(None, description="お気に入りフラグ")
    citation_count: int | None = Field(None, ge=0, description="被引用数")
    category_id: int | None = Field(None, description="カテゴリID")
    tag_ids: list[int] | None = Field(None, description="タグIDのリスト")


class PaperInDBBase(PaperBase):
    """Base paper schema with database fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int | None = None
    read_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class Paper(PaperInDBBase):
    """Paper schema for API responses."""

    pass


class PaperInDB(PaperInDBBase):
    """Paper schema for database storage."""

    pass


class PaperList(BaseModel):
    """Paper list response schema."""

    items: list[Paper]
    total: int
    page: int
    size: int
    pages: int


class PaperRating(BaseModel):
    """Paper rating schema."""

    rating: int = Field(..., ge=1, le=5, description="評価(1-5)")


class PaperStatus(BaseModel):
    """Paper reading status schema."""

    reading_status: str = Field(
        ...,
        description="読書ステータス (to_read, reading, completed, skipped)",
    )
