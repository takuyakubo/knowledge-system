"""CRUD operations for Category model."""

from typing import Any

from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    """Category CRUD operations."""

    def get_by_slug(self, db: Session, *, slug: str) -> Category | None:
        """スラッグでカテゴリを取得."""
        return db.query(Category).filter(Category.slug == slug).first()

    def get_by_path(self, db: Session, *, path: str) -> Category | None:
        """パスでカテゴリを取得."""
        return db.query(Category).filter(Category.path == path).first()

    def get_root_categories(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[Category]:
        """ルートカテゴリを取得."""
        return (
            db.query(Category)
            .filter(Category.parent_id.is_(None), Category.is_active.is_(True))
            .order_by(Category.sort_order, Category.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_children(
        self, db: Session, *, parent_id: int, skip: int = 0, limit: int = 100
    ) -> list[Category]:
        """指定カテゴリの子カテゴリを取得."""
        return (
            db.query(Category)
            .filter(Category.parent_id == parent_id, Category.is_active.is_(True))
            .order_by(Category.sort_order, Category.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_level(
        self, db: Session, *, level: int, skip: int = 0, limit: int = 100
    ) -> list[Category]:
        """指定レベルのカテゴリを取得."""
        return (
            db.query(Category)
            .filter(Category.level == level, Category.is_active.is_(True))
            .order_by(Category.sort_order, Category.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_ancestors(self, db: Session, *, category_id: int) -> list[Category]:
        """祖先カテゴリを取得（パンくずリスト用）."""
        category = self.get(db, id=category_id)
        if not category:
            return []

        ancestors = []
        current = category.parent

        while current:
            ancestors.insert(0, current)
            current = current.parent

        return ancestors

    def get_descendants(
        self, db: Session, *, category_id: int, include_self: bool = False
    ) -> list[Category]:
        """子孫カテゴリを全て取得."""
        if include_self:
            # 自分も含める場合、パスを使って効率的に検索
            category = self.get(db, id=category_id)
            if not category:
                return []

            return (
                db.query(Category)
                .filter(
                    or_(
                        Category.id == category_id,
                        Category.path.like(f"{category.path}/%"),
                    )
                )
                .order_by(Category.level, Category.sort_order, Category.name)
                .all()
            )
        else:
            category = self.get(db, id=category_id)
            if not category:
                return []

            return (
                db.query(Category)
                .filter(Category.path.like(f"{category.path}/%"))
                .order_by(Category.level, Category.sort_order, Category.name)
                .all()
            )

    def get_category_tree(self, db: Session) -> list[Category]:
        """階層構造を保った完全なカテゴリツリーを取得."""
        # 全てのアクティブなカテゴリを階層順で取得
        categories = (
            db.query(Category)
            .filter(Category.is_active.is_(True))
            .order_by(Category.level, Category.sort_order, Category.name)
            .options(joinedload(Category.children))
            .all()
        )

        # ルートカテゴリのみを返す（関連する子は自動で含まれる）
        return [cat for cat in categories if cat.parent_id is None]

    def search(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> list[Category]:
        """カテゴリを検索."""
        search_filter = or_(
            Category.name.ilike(f"%{query}%"),
            Category.description.ilike(f"%{query}%"),
            Category.path.ilike(f"%{query}%"),
        )

        return (
            db.query(Category)
            .filter(search_filter, Category.is_active.is_(True))
            .order_by(Category.level, Category.sort_order, Category.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_slug(self, db: Session, *, obj_in: CategoryCreate) -> Category:
        """スラッグ自動生成付きでカテゴリを作成."""
        obj_in_data = obj_in.model_dump()

        # スラッグが未指定の場合は自動生成
        if not obj_in_data.get("slug"):
            obj_in_data["slug"] = Category.create_slug_from_name(obj_in_data["name"])

        # スラッグの重複チェックと修正
        base_slug = obj_in_data["slug"]
        counter = 1
        while self.get_by_slug(db, slug=obj_in_data["slug"]):
            obj_in_data["slug"] = f"{base_slug}-{counter}"
            counter += 1

        # 親カテゴリの検証と階層情報の設定
        if obj_in_data.get("parent_id"):
            parent = self.get(db, id=obj_in_data["parent_id"])
            if not parent:
                raise ValueError(
                    f"Parent category with ID {obj_in_data['parent_id']} not found"
                )
            if not parent.is_active:
                raise ValueError("Cannot create category under inactive parent")

        db_obj = Category(**obj_in_data)

        # 階層情報を更新
        db_obj.update_path()

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # カウント更新
        self._update_parent_counts(db, db_obj)

        return db_obj

    def move_category(
        self, db: Session, *, category_id: int, new_parent_id: int | None
    ) -> Category | None:
        """カテゴリを別の親の下に移動."""
        category = self.get(db, id=category_id)
        if not category:
            return None

        # 新しい親の検証
        if new_parent_id:
            new_parent = self.get(db, id=new_parent_id)
            if not new_parent:
                raise ValueError(f"Parent category with ID {new_parent_id} not found")
            if not new_parent.is_active:
                raise ValueError("Cannot move category under inactive parent")

            # 循環参照チェック
            if category_id in new_parent.get_all_descendants_ids():
                raise ValueError("Cannot move category under its own descendant")

        # 移動実行
        old_parent = category.parent
        category.move_to_parent(new_parent if new_parent_id else None)

        db.add(category)

        # 子カテゴリのパスも更新
        descendants = self.get_descendants(db, category_id=category_id)
        for descendant in descendants:
            descendant.update_path()
            db.add(descendant)

        db.commit()

        # 関連するカテゴリのカウントを更新
        self._update_parent_counts(db, category)
        if old_parent:
            self._update_parent_counts(db, old_parent)

        db.refresh(category)
        return category

    def bulk_update_sort_order(
        self, db: Session, *, updates: list[dict[str, Any]]
    ) -> list[Category]:
        """複数カテゴリの表示順序を一括更新."""
        updated_categories = []

        for update in updates:
            category_id = update.get("id")
            sort_order = update.get("sort_order")

            if category_id and sort_order is not None:
                category = self.get(db, id=category_id)
                if category:
                    category.sort_order = sort_order
                    db.add(category)
                    updated_categories.append(category)

        db.commit()

        for category in updated_categories:
            db.refresh(category)

        return updated_categories

    def get_popular_categories(
        self, db: Session, *, limit: int = 10, min_content: int = 1
    ) -> list[Category]:
        """人気カテゴリを取得（コンテンツ数順）."""
        return (
            db.query(Category)
            .filter(
                Category.is_active.is_(True),
                (Category.article_count + Category.paper_count) >= min_content,
            )
            .order_by(
                desc(Category.article_count + Category.paper_count), Category.name
            )
            .limit(limit)
            .all()
        )

    def get_empty_categories(self, db: Session) -> list[Category]:
        """コンテンツが空のカテゴリを取得."""
        return (
            db.query(Category)
            .filter(
                Category.is_active.is_(True),
                Category.article_count == 0,
                Category.paper_count == 0,
            )
            .order_by(Category.level, Category.name)
            .all()
        )

    def update_all_counts(self, db: Session) -> int:
        """全カテゴリのコンテンツ数を再計算."""
        updated_count = 0
        categories = db.query(Category).all()

        for category in categories:
            old_article_count = category.article_count
            old_paper_count = category.paper_count

            category.update_counts()

            if (
                category.article_count != old_article_count
                or category.paper_count != old_paper_count
            ):
                db.add(category)
                updated_count += 1

        db.commit()
        return updated_count

    def get_stats(self, db: Session) -> dict[str, Any]:
        """カテゴリの統計情報を取得."""
        total_categories = db.query(func.count(Category.id)).scalar()
        active_categories = (
            db.query(func.count(Category.id))
            .filter(Category.is_active.is_(True))
            .scalar()
        )
        root_categories = (
            db.query(func.count(Category.id))
            .filter(Category.parent_id.is_(None), Category.is_active.is_(True))
            .scalar()
        )

        # 最大階層深度
        max_depth = db.query(func.max(Category.level)).scalar() or 0

        # 階層別カテゴリ数
        level_counts = (
            db.query(Category.level, func.count(Category.id))
            .filter(Category.is_active.is_(True))
            .group_by(Category.level)
            .all()
        )
        categories_by_level = {level: count for level, count in level_counts}

        # 人気カテゴリ
        popular_categories = self.get_popular_categories(db, limit=5)
        top_categories = [
            {
                "id": cat.id,
                "name": cat.name,
                "content_count": cat.total_content_count,
                "path": cat.path,
            }
            for cat in popular_categories
        ]

        return {
            "total_categories": total_categories,
            "active_categories": active_categories,
            "root_categories": root_categories,
            "max_depth": max_depth,
            "categories_by_level": categories_by_level,
            "top_categories": top_categories,
        }

    def deactivate(self, db: Session, *, category_id: int) -> Category | None:
        """カテゴリを無効化（削除ではなく非活性）."""
        category = self.get(db, id=category_id)
        if not category:
            return None

        # 子カテゴリも一緒に無効化
        descendants = self.get_descendants(db, category_id=category_id)
        for descendant in descendants:
            descendant.is_active = False
            db.add(descendant)

        category.is_active = False
        db.add(category)
        db.commit()
        db.refresh(category)

        return category

    def activate(self, db: Session, *, category_id: int) -> Category | None:
        """カテゴリを有効化."""
        category = self.get(db, id=category_id)
        if not category:
            return None

        # 親カテゴリが無効の場合は有効化できない
        if category.parent and not category.parent.is_active:
            raise ValueError("Cannot activate category with inactive parent")

        category.is_active = True
        db.add(category)
        db.commit()
        db.refresh(category)

        return category

    def get_multi_with_filters(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Category]:
        """複数フィルターでカテゴリを取得."""
        query = db.query(Category)

        if filters:
            if filters.get("is_active") is not None:
                query = query.filter(Category.is_active.is_(filters["is_active"]))
            if filters.get("is_system") is not None:
                query = query.filter(Category.is_system.is_(filters["is_system"]))
            if filters.get("parent_id") is not None:
                query = query.filter(Category.parent_id == filters["parent_id"])
            if filters.get("level") is not None:
                query = query.filter(Category.level == filters["level"])
            if filters.get("min_content") is not None:
                min_content = filters["min_content"]
                query = query.filter(
                    (Category.article_count + Category.paper_count) >= min_content
                )
            if filters.get("color") is not None:
                query = query.filter(Category.color == filters["color"])

        return (
            query.order_by(Category.level, Category.sort_order, Category.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def _update_parent_counts(self, db: Session, category: Category) -> None:
        """親カテゴリのカウントを更新."""
        current = category.parent
        while current:
            current.update_counts()
            db.add(current)
            current = current.parent


category = CRUDCategory(Category)
