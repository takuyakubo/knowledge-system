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
]
