"""Main API router for v1."""

from fastapi import APIRouter

from app.api.v1 import articles, auth, categories, files, papers, tags

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Main API endpoints
api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(papers.router, prefix="/papers", tags=["papers"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
