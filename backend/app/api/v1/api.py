"""Main API router for v1."""

from fastapi import APIRouter

from app.api.v1 import articles, papers, tags

api_router = APIRouter()

api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
api_router.include_router(papers.router, prefix="/papers", tags=["papers"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
