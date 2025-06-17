"""CRUD operations for Tag model."""

from typing import Any

from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate


class CRUDTag(CRUDBase[Tag, TagCreate, TagUpdate]):
    """Tag CRUD operations."""

    def get_by_name(self, db: Session, *, name: str) -> Tag | None:
        """タグ名でタグを取得."""
        return db.query(Tag).filter(Tag.name == name).first()

    def get_by_slug(self, db: Session, *, slug: str) -> Tag | None:
        """スラッグでタグを取得."""
        return db.query(Tag).filter(Tag.slug == slug).first()

    def get_active_tags(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[Tag]:
        """有効なタグを取得."""
        return (
            db.query(Tag)
            .filter(Tag.is_active.is_(True))
            .order_by(desc(Tag.usage_count), Tag.sort_order, Tag.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_system_tags(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[Tag]:
        """システムタグを取得."""
        return (
            db.query(Tag)
            .filter(Tag.is_system.is_(True))
            .order_by(Tag.sort_order, Tag.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_popular_tags(
        self, db: Session, *, limit: int = 20, min_usage: int = 1
    ) -> list[Tag]:
        """人気タグを使用回数順で取得."""
        return (
            db.query(Tag)
            .filter(Tag.is_active.is_(True), Tag.usage_count >= min_usage)
            .order_by(desc(Tag.usage_count), Tag.name)
            .limit(limit)
            .all()
        )

    def search(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> list[Tag]:
        """タグを検索."""
        search_filter = or_(
            Tag.name.ilike(f"%{query}%"),
            Tag.description.ilike(f"%{query}%"),
        )
        return (
            db.query(Tag)
            .filter(search_filter, Tag.is_active.is_(True))
            .order_by(desc(Tag.usage_count), Tag.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_slug(self, db: Session, *, obj_in: TagCreate) -> Tag:
        """スラッグ自動生成付きでタグを作成."""
        obj_in_data = obj_in.model_dump()

        # スラッグが未指定の場合は自動生成
        if not obj_in_data.get("slug"):
            obj_in_data["slug"] = Tag.create_slug_from_name(obj_in_data["name"])

        # スラッグの重複チェックと修正
        base_slug = obj_in_data["slug"]
        counter = 1
        while self.get_by_slug(db, slug=obj_in_data["slug"]):
            obj_in_data["slug"] = f"{base_slug}-{counter}"
            counter += 1

        db_obj = Tag(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def bulk_create_from_names(self, db: Session, *, tag_names: list[str]) -> list[Tag]:
        """タグ名のリストから一括作成（既存は取得）."""
        tags = []
        processed_names = set()  # 重複防止用

        for tag_name in tag_names:
            cleaned_name = tag_name.strip()
            if not cleaned_name or cleaned_name in processed_names:
                continue

            processed_names.add(cleaned_name)

            # 既存チェック
            tag = self.get_by_name(db, name=cleaned_name)
            if not tag:
                # 新規作成
                tag_create = TagCreate(name=cleaned_name)
                tag = self.create_with_slug(db, obj_in=tag_create)

            tags.append(tag)

        return tags

    def increment_usage(self, db: Session, *, tag_id: int) -> Tag | None:
        """使用回数をインクリメント."""
        tag = self.get(db, id=tag_id)
        if tag:
            tag.increment_usage_count()
            db.add(tag)
            db.commit()
            db.refresh(tag)
        return tag

    def decrement_usage(self, db: Session, *, tag_id: int) -> Tag | None:
        """使用回数をデクリメント."""
        tag = self.get(db, id=tag_id)
        if tag:
            tag.decrement_usage_count()
            db.add(tag)
            db.commit()
            db.refresh(tag)
        return tag

    def update_usage_counts(self, db: Session) -> int:
        """全タグの使用回数を実際の関連数から再計算."""
        # すべてのタグに対して実際の使用回数を計算
        updated_count = 0
        tags = db.query(Tag).all()

        for tag in tags:
            actual_count = len(tag.articles) + len(tag.papers)
            if tag.usage_count != actual_count:
                tag.usage_count = actual_count
                db.add(tag)
                updated_count += 1

        db.commit()
        return updated_count

    def deactivate(self, db: Session, *, tag_id: int) -> Tag | None:
        """タグを無効化（削除ではなく非活性）."""
        tag = self.get(db, id=tag_id)
        if tag:
            tag.is_active = False
            db.add(tag)
            db.commit()
            db.refresh(tag)
        return tag

    def activate(self, db: Session, *, tag_id: int) -> Tag | None:
        """タグを有効化."""
        tag = self.get(db, id=tag_id)
        if tag:
            tag.is_active = True
            db.add(tag)
            db.commit()
            db.refresh(tag)
        return tag

    def merge_tags(
        self, db: Session, *, source_ids: list[int], target_id: int
    ) -> Tag | None:
        """複数のタグを1つのタグに統合."""
        target_tag = self.get(db, id=target_id)
        if not target_tag:
            return None

        for source_id in source_ids:
            if source_id == target_id:
                continue

            source_tag = self.get(db, id=source_id)
            if not source_tag:
                continue

            # 記事の関連を移行
            for article in source_tag.articles:
                if target_tag not in article.tags:
                    article.tags.append(target_tag)
                article.tags.remove(source_tag)

            # 論文の関連を移行
            for paper in source_tag.papers:
                if target_tag not in paper.tags:
                    paper.tags.append(target_tag)
                paper.tags.remove(source_tag)

            # ソースタグを削除
            db.delete(source_tag)

        # 使用回数を更新
        target_tag.update_usage_count()
        db.add(target_tag)
        db.commit()
        db.refresh(target_tag)

        return target_tag

    def get_usage_stats(self, db: Session) -> list[dict[str, Any]]:
        """タグの使用統計を取得."""
        # サブクエリで記事と論文の数をカウント
        article_counts = (
            db.query(
                Tag.id,
                func.count(func.distinct("articles.id")).label("article_count"),
            )
            .outerjoin(Tag.articles)
            .group_by(Tag.id)
            .subquery()
        )

        paper_counts = (
            db.query(
                Tag.id,
                func.count(func.distinct("papers.id")).label("paper_count"),
            )
            .outerjoin(Tag.papers)
            .group_by(Tag.id)
            .subquery()
        )

        # メインクエリ
        stats = (
            db.query(
                Tag.id,
                Tag.name,
                Tag.usage_count,
                func.coalesce(article_counts.c.article_count, 0).label("article_count"),
                func.coalesce(paper_counts.c.paper_count, 0).label("paper_count"),
            )
            .outerjoin(article_counts, Tag.id == article_counts.c.id)
            .outerjoin(paper_counts, Tag.id == paper_counts.c.id)
            .filter(Tag.is_active.is_(True))
            .order_by(desc(Tag.usage_count), Tag.name)
            .all()
        )

        return [
            {
                "tag_id": stat.id,
                "tag_name": stat.name,
                "usage_count": stat.usage_count,
                "article_count": stat.article_count,
                "paper_count": stat.paper_count,
            }
            for stat in stats
        ]

    def get_unused_tags(self, db: Session) -> list[Tag]:
        """使用されていないタグを取得."""
        return (
            db.query(Tag)
            .filter(Tag.usage_count == 0, Tag.is_active.is_(True))
            .order_by(Tag.name)
            .all()
        )

    def get_multi_with_filters(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Tag]:
        """複数フィルターでタグを取得."""
        query = db.query(Tag)

        if filters:
            if filters.get("is_active") is not None:
                query = query.filter(Tag.is_active.is_(filters["is_active"]))
            if filters.get("is_system") is not None:
                query = query.filter(Tag.is_system.is_(filters["is_system"]))
            if filters.get("min_usage") is not None:
                query = query.filter(Tag.usage_count >= filters["min_usage"])
            if filters.get("color") is not None:
                query = query.filter(Tag.color == filters["color"])

        return (
            query.order_by(desc(Tag.usage_count), Tag.sort_order, Tag.name)
            .offset(skip)
            .limit(limit)
            .all()
        )


tag = CRUDTag(Tag)
