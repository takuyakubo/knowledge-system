"""Article CRUD operations."""

from datetime import datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate


class CRUDArticle(CRUDBase[Article, ArticleCreate, ArticleUpdate]):
    """Article CRUD operations."""

    def get_by_slug(self, db: Session, *, slug: str) -> Article | None:
        """Get article by slug."""
        return db.query(Article).filter(Article.slug == slug).first()

    def get_published(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[Article]:
        """Get published articles only."""
        return (
            db.query(Article)
            .filter(and_(Article.is_public.is_(True), Article.status == "published"))
            .order_by(Article.published_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_category(
        self, db: Session, *, category_id: int, skip: int = 0, limit: int = 100
    ) -> list[Article]:
        """Get articles by category."""
        return (
            db.query(Article)
            .filter(Article.category_id == category_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search(
        self,
        db: Session,
        *,
        query: str,
        skip: int = 0,
        limit: int = 100,
        published_only: bool = True,
    ) -> list[Article]:
        """Search articles by title and content."""
        search_filter = or_(
            Article.title.ilike(f"%{query}%"),
            Article.content.ilike(f"%{query}%"),
            Article.summary.ilike(f"%{query}%"),
        )

        base_query = db.query(Article).filter(search_filter)

        if published_only:
            base_query = base_query.filter(
                and_(Article.is_public.is_(True), Article.status == "published")
            )

        return base_query.offset(skip).limit(limit).all()

    def publish(self, db: Session, *, db_obj: Article) -> Article:
        """Publish an article."""
        db_obj.status = "published"
        db_obj.is_public = True
        db_obj.published_at = datetime.now()

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def unpublish(self, db: Session, *, db_obj: Article) -> Article:
        """Unpublish an article."""
        db_obj.is_public = False

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def increment_view_count(self, db: Session, *, db_obj: Article) -> Article:
        """Increment view count."""
        db_obj.view_count += 1

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def increment_like_count(self, db: Session, *, db_obj: Article) -> Article:
        """Increment like count."""
        db_obj.like_count += 1

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_popular(
        self, db: Session, *, skip: int = 0, limit: int = 10
    ) -> list[Article]:
        """Get popular articles by view count."""
        return (
            db.query(Article)
            .filter(and_(Article.is_public.is_(True), Article.status == "published"))
            .order_by(Article.view_count.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_recent(
        self, db: Session, *, skip: int = 0, limit: int = 10
    ) -> list[Article]:
        """Get recent articles."""
        return (
            db.query(Article)
            .filter(and_(Article.is_public.is_(True), Article.status == "published"))
            .order_by(Article.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


article = CRUDArticle(Article)
