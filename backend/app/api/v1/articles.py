"""Article API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.deps import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.Article])
def read_articles(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit items"),
    published_only: bool = Query(True, description="Published articles only"),
    category_id: int | None = Query(None, description="Filter by category"),
    search: str | None = Query(None, description="Search query"),
) -> Any:
    """Get articles with optional filtering."""
    if search:
        articles = crud.article.search(
            db, query=search, skip=skip, limit=limit, published_only=published_only
        )
    elif category_id:
        articles = crud.article.get_by_category(
            db, category_id=category_id, skip=skip, limit=limit
        )
    elif published_only:
        articles = crud.article.get_published(db, skip=skip, limit=limit)
    else:
        articles = crud.article.get_multi(db, skip=skip, limit=limit)

    return articles


@router.post("/", response_model=schemas.Article)
def create_article(
    *,
    db: Session = Depends(get_db),
    article_in: schemas.ArticleCreate,
) -> Any:
    """Create new article."""
    # Generate slug from title if not provided
    if not article_in.slug and article_in.title:
        from slugify import slugify

        potential_slug = slugify(article_in.title)

        # Check if slug exists and make it unique
        existing = crud.article.get_by_slug(db, slug=potential_slug)
        if existing:
            counter = 1
            while existing:
                test_slug = f"{potential_slug}-{counter}"
                existing = crud.article.get_by_slug(db, slug=test_slug)
                counter += 1
            potential_slug = test_slug

        article_in.slug = potential_slug

    article = crud.article.create(db=db, obj_in=article_in)
    return article


@router.get("/popular", response_model=list[schemas.Article])
def read_popular_articles(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(10, ge=1, le=100, description="Limit items"),
) -> Any:
    """Get popular articles by view count."""
    articles = crud.article.get_popular(db, skip=skip, limit=limit)
    return articles


@router.get("/recent", response_model=list[schemas.Article])
def read_recent_articles(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(10, ge=1, le=100, description="Limit items"),
) -> Any:
    """Get recent articles."""
    articles = crud.article.get_recent(db, skip=skip, limit=limit)
    return articles


@router.get("/{article_id}", response_model=schemas.Article)
def read_article(
    *,
    db: Session = Depends(get_db),
    article_id: int,
    increment_views: bool = Query(False, description="Increment view count"),
) -> Any:
    """Get article by ID."""
    article = crud.article.get(db=db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if increment_views:
        article = crud.article.increment_view_count(db=db, db_obj=article)

    return article


@router.get("/slug/{slug}", response_model=schemas.Article)
def read_article_by_slug(
    *,
    db: Session = Depends(get_db),
    slug: str,
    increment_views: bool = Query(False, description="Increment view count"),
) -> Any:
    """Get article by slug."""
    article = crud.article.get_by_slug(db=db, slug=slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if increment_views:
        article = crud.article.increment_view_count(db=db, db_obj=article)

    return article


@router.put("/{article_id}", response_model=schemas.Article)
def update_article(
    *,
    db: Session = Depends(get_db),
    article_id: int,
    article_in: schemas.ArticleUpdate,
) -> Any:
    """Update article."""
    article = crud.article.get(db=db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article = crud.article.update(db=db, db_obj=article, obj_in=article_in)
    return article


@router.post("/{article_id}/publish", response_model=schemas.Article)
def publish_article(
    *,
    db: Session = Depends(get_db),
    article_id: int,
) -> Any:
    """Publish article."""
    article = crud.article.get(db=db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article = crud.article.publish(db=db, db_obj=article)
    return article


@router.post("/{article_id}/unpublish", response_model=schemas.Article)
def unpublish_article(
    *,
    db: Session = Depends(get_db),
    article_id: int,
) -> Any:
    """Unpublish article."""
    article = crud.article.get(db=db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article = crud.article.unpublish(db=db, db_obj=article)
    return article


@router.post("/{article_id}/like", response_model=schemas.Article)
def like_article(
    *,
    db: Session = Depends(get_db),
    article_id: int,
) -> Any:
    """Like article (increment like count)."""
    article = crud.article.get(db=db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article = crud.article.increment_like_count(db=db, db_obj=article)
    return article


@router.delete("/{article_id}")
def delete_article(
    *,
    db: Session = Depends(get_db),
    article_id: int,
) -> Any:
    """Delete article."""
    article = crud.article.get(db=db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article = crud.article.remove(db=db, id=article_id)
    return {"message": "Article deleted successfully"}
