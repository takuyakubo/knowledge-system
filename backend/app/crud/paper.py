"""CRUD operations for Paper model."""

from datetime import datetime
from typing import Any

from sqlalchemy import and_, desc, or_
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.paper import Paper
from app.models.tag import Tag
from app.schemas.paper import PaperCreate, PaperUpdate


class CRUDPaper(CRUDBase[Paper, PaperCreate, PaperUpdate]):
    """Paper CRUD operations."""

    def get_by_doi(self, db: Session, *, doi: str) -> Paper | None:
        """DOIで論文を取得."""
        return db.query(Paper).filter(Paper.doi == doi).first()

    def get_by_arxiv_id(self, db: Session, *, arxiv_id: str) -> Paper | None:
        """arXiv IDで論文を取得."""
        return db.query(Paper).filter(Paper.arxiv_id == arxiv_id).first()

    def get_by_pmid(self, db: Session, *, pmid: str) -> Paper | None:
        """PubMed IDで論文を取得."""
        return db.query(Paper).filter(Paper.pmid == pmid).first()

    def search(
        self,
        db: Session,
        *,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Paper]:
        """論文を検索."""
        search_filter = or_(
            Paper.title.ilike(f"%{query}%"),
            Paper.abstract.ilike(f"%{query}%"),
            Paper.authors.ilike(f"%{query}%"),
            Paper.journal.ilike(f"%{query}%"),
            Paper.conference.ilike(f"%{query}%"),
            Paper.personal_notes.ilike(f"%{query}%"),
        )
        return (
            db.query(Paper)
            .filter(search_filter)
            .options(joinedload(Paper.tags), joinedload(Paper.category))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_reading_status(
        self,
        db: Session,
        *,
        reading_status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Paper]:
        """読書ステータスで論文を取得."""
        return (
            db.query(Paper)
            .filter(Paper.reading_status == reading_status)
            .options(joinedload(Paper.tags), joinedload(Paper.category))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_favorites(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Paper]:
        """お気に入り論文を取得."""
        return (
            db.query(Paper)
            .filter(Paper.is_favorite.is_(True))
            .options(joinedload(Paper.tags), joinedload(Paper.category))
            .order_by(desc(Paper.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_year(
        self,
        db: Session,
        *,
        year: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Paper]:
        """発行年で論文を取得."""
        return (
            db.query(Paper)
            .filter(Paper.publication_year == year)
            .options(joinedload(Paper.tags), joinedload(Paper.category))
            .order_by(desc(Paper.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_year_range(
        self,
        db: Session,
        *,
        start_year: int,
        end_year: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Paper]:
        """年範囲で論文を取得."""
        return (
            db.query(Paper)
            .filter(
                and_(
                    Paper.publication_year >= start_year,
                    Paper.publication_year <= end_year,
                )
            )
            .options(joinedload(Paper.tags), joinedload(Paper.category))
            .order_by(desc(Paper.publication_year), desc(Paper.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_priority(
        self,
        db: Session,
        *,
        min_priority: int = 1,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Paper]:
        """優先度で論文を取得."""
        return (
            db.query(Paper)
            .filter(Paper.priority >= min_priority)
            .options(joinedload(Paper.tags), joinedload(Paper.category))
            .order_by(desc(Paper.priority), desc(Paper.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_category(
        self,
        db: Session,
        *,
        category_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Paper]:
        """カテゴリで論文を取得."""
        return (
            db.query(Paper)
            .filter(Paper.category_id == category_id)
            .options(joinedload(Paper.tags), joinedload(Paper.category))
            .order_by(desc(Paper.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_tags(
        self, db: Session, *, obj_in: PaperCreate, tag_ids: list[int] | None = None
    ) -> Paper:
        """タグ付きで論文を作成."""
        obj_in_data = obj_in.model_dump(exclude={"tag_ids"})
        db_obj = Paper(**obj_in_data)

        if tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            db_obj.tags = tags

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_with_tags(
        self,
        db: Session,
        *,
        db_obj: Paper,
        obj_in: PaperUpdate,
    ) -> Paper:
        """タグ付きで論文を更新."""
        obj_data = obj_in.model_dump(exclude_unset=True)
        tag_ids = obj_data.pop("tag_ids", None)

        # 基本フィールドを更新
        for field, value in obj_data.items():
            setattr(db_obj, field, value)

        # タグを更新
        if tag_ids is not None:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            db_obj.tags = tags

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def set_rating(self, db: Session, *, db_obj: Paper, rating: int) -> Paper:
        """論文の評価を設定."""
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")

        db_obj.rating = rating
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def set_reading_status(self, db: Session, *, db_obj: Paper, status: str) -> Paper:
        """読書ステータスを設定."""
        valid_statuses = ["to_read", "reading", "completed", "skipped"]
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")

        db_obj.reading_status = status
        if status == "completed":
            db_obj.read_at = datetime.now()

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def toggle_favorite(self, db: Session, *, db_obj: Paper) -> Paper:
        """お気に入り状態を切り替え."""
        db_obj.is_favorite = not db_obj.is_favorite
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def increment_citation_count(self, db: Session, *, db_obj: Paper) -> Paper:
        """被引用数を増加."""
        db_obj.citation_count += 1
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_with_filters(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Paper]:
        """複数フィルターで論文を取得."""
        query = db.query(Paper).options(
            joinedload(Paper.tags), joinedload(Paper.category)
        )

        if filters:
            if filters.get("category_id") is not None:
                query = query.filter(Paper.category_id == filters["category_id"])
            if filters.get("reading_status") is not None:
                query = query.filter(Paper.reading_status == filters["reading_status"])
            if filters.get("paper_type") is not None:
                query = query.filter(Paper.paper_type == filters["paper_type"])
            if filters.get("is_favorite") is not None:
                query = query.filter(Paper.is_favorite.is_(filters["is_favorite"]))
            if filters.get("min_priority") is not None:
                query = query.filter(Paper.priority >= filters["min_priority"])
            if filters.get("publication_year") is not None:
                query = query.filter(
                    Paper.publication_year == filters["publication_year"]
                )

        return query.order_by(desc(Paper.created_at)).offset(skip).limit(limit).all()


paper = CRUDPaper(Paper)
