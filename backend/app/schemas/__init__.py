"""Pydantic schemas package."""

from app.schemas.article import (
    Article,
    ArticleCreate,
    ArticleInDB,
    ArticleList,
    ArticlePublish,
    ArticleUpdate,
)
from app.schemas.paper import (
    Paper,
    PaperCreate,
    PaperInDB,
    PaperList,
    PaperRating,
    PaperStatus,
    PaperUpdate,
)
from app.schemas.tag import (
    Tag,
    TagBulkCreate,
    TagCreate,
    TagInDB,
    TagList,
    TagMerge,
    TagUpdate,
    TagUsageStats,
)

__all__ = [
    "Article",
    "ArticleCreate",
    "ArticleUpdate",
    "ArticleInDB",
    "ArticleList",
    "ArticlePublish",
    "Paper",
    "PaperCreate",
    "PaperUpdate",
    "PaperInDB",
    "PaperList",
    "PaperRating",
    "PaperStatus",
    "Tag",
    "TagCreate",
    "TagUpdate",
    "TagInDB",
    "TagList",
    "TagBulkCreate",
    "TagMerge",
    "TagUsageStats",
]
