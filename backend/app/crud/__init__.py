"""CRUD operations package."""

from app.crud.article import article
from app.crud.paper import paper
from app.crud.tag import tag

__all__ = ["article", "paper", "tag"]
