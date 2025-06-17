"""CRUD operations package."""

from app.crud.article import article
from app.crud.category import category
from app.crud.file import file
from app.crud.paper import paper
from app.crud.tag import tag

__all__ = ["article", "category", "file", "paper", "tag"]
