"""Main API router for v1."""

from fastapi import APIRouter

from app.api.v1 import articles

api_router = APIRouter()

api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
