"""Category API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import category as crud_category
from app.deps import get_current_user, get_db
from app.schemas import category as schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.Category])
def get_categories(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する件数"),
    is_active: bool | None = Query(None, description="有効フラグでフィルター"),
    is_system: bool | None = Query(None, description="システムカテゴリでフィルター"),
    parent_id: int | None = Query(None, description="親カテゴリIDでフィルター"),
    level: int | None = Query(None, ge=0, description="階層レベルでフィルター"),
    min_content: int | None = Query(
        None, ge=0, description="最小コンテンツ数でフィルター"
    ),
    color: str | None = Query(None, description="色でフィルター"),
) -> list[schemas.Category]:
    """カテゴリ一覧を取得."""
    filters = {
        "is_active": is_active,
        "is_system": is_system,
        "parent_id": parent_id,
        "level": level,
        "min_content": min_content,
        "color": color,
    }
    # None値を除去
    filters = {k: v for k, v in filters.items() if v is not None}

    return crud_category.get_multi_with_filters(
        db, skip=skip, limit=limit, filters=filters
    )


@router.get("/tree", response_model=list[schemas.CategoryTree])
def get_category_tree(
    db: Session = Depends(get_db),
) -> list[schemas.CategoryTree]:
    """階層構造を保ったカテゴリツリーを取得."""
    return crud_category.get_category_tree(db)


@router.get("/roots", response_model=list[schemas.Category])
def get_root_categories(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する件数"),
) -> list[schemas.Category]:
    """ルートカテゴリ一覧を取得."""
    return crud_category.get_root_categories(db, skip=skip, limit=limit)


@router.get("/search", response_model=schemas.CategorySearchResult)
def search_categories(
    q: str = Query(..., min_length=1, description="検索クエリ"),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する件数"),
) -> schemas.CategorySearchResult:
    """カテゴリを検索."""
    categories = crud_category.search(db, query=q, skip=skip, limit=limit)

    # 総件数を取得（実装を簡単にするため、実際のカウントクエリは省略）
    total = len(categories)

    return schemas.CategorySearchResult(
        categories=categories,
        total=total,
        page=skip // limit + 1,
        size=limit,
        has_next=len(categories) == limit,
    )


@router.get("/popular", response_model=list[schemas.Category])
def get_popular_categories(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50, description="取得する件数"),
    min_content: int = Query(1, ge=0, description="最小コンテンツ数"),
) -> list[schemas.Category]:
    """人気カテゴリを取得."""
    return crud_category.get_popular_categories(
        db, limit=limit, min_content=min_content
    )


@router.get("/empty", response_model=list[schemas.Category])
def get_empty_categories(
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[schemas.Category]:
    """コンテンツが空のカテゴリを取得."""
    return crud_category.get_empty_categories(db)


@router.get("/stats", response_model=schemas.CategoryStats)
def get_category_stats(
    db: Session = Depends(get_db),
) -> schemas.CategoryStats:
    """カテゴリの統計情報を取得."""
    stats = crud_category.get_stats(db)
    return schemas.CategoryStats(**stats)


@router.get("/{category_id}", response_model=schemas.Category)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
) -> schemas.Category:
    """指定されたIDのカテゴリを取得."""
    category = crud_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/{category_id}/children", response_model=list[schemas.Category])
def get_category_children(
    category_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する件数"),
) -> list[schemas.Category]:
    """指定カテゴリの子カテゴリを取得."""
    # 親カテゴリの存在確認
    parent = crud_category.get(db, id=category_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Parent category not found")

    return crud_category.get_children(db, parent_id=category_id, skip=skip, limit=limit)


@router.get("/{category_id}/descendants", response_model=list[schemas.Category])
def get_category_descendants(
    category_id: int,
    db: Session = Depends(get_db),
    include_self: bool = Query(False, description="自分自身も含めるか"),
) -> list[schemas.Category]:
    """指定カテゴリの子孫カテゴリを全て取得."""
    # カテゴリの存在確認
    category = crud_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return crud_category.get_descendants(
        db, category_id=category_id, include_self=include_self
    )


@router.get("/{category_id}/ancestors", response_model=list[schemas.Category])
def get_category_ancestors(
    category_id: int,
    db: Session = Depends(get_db),
) -> list[schemas.Category]:
    """指定カテゴリの祖先カテゴリを取得（パンくずリスト用）."""
    # カテゴリの存在確認
    category = crud_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return crud_category.get_ancestors(db, category_id=category_id)


@router.get("/slug/{slug}", response_model=schemas.Category)
def get_category_by_slug(
    slug: str,
    db: Session = Depends(get_db),
) -> schemas.Category:
    """スラッグでカテゴリを取得."""
    category = crud_category.get_by_slug(db, slug=slug)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/path/{path:path}", response_model=schemas.Category)
def get_category_by_path(
    path: str,
    db: Session = Depends(get_db),
) -> schemas.Category:
    """パスでカテゴリを取得."""
    # パスの正規化（先頭にスラッシュを追加）
    if not path.startswith("/"):
        path = f"/{path}"

    category = crud_category.get_by_path(db, path=path)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=schemas.Category)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: schemas.CategoryCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> schemas.Category:
    """新しいカテゴリを作成."""
    try:
        return crud_category.create_with_slug(db, obj_in=category_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{category_id}", response_model=schemas.Category)
def update_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    category_in: schemas.CategoryUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> schemas.Category:
    """カテゴリを更新."""
    category = crud_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    try:
        return crud_category.update(db, db_obj=category, obj_in=category_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/{category_id}/move", response_model=schemas.Category)
def move_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    move_data: schemas.CategoryMove,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> schemas.Category:
    """カテゴリを別の親の下に移動."""
    try:
        category = crud_category.move_category(
            db, category_id=category_id, new_parent_id=move_data.new_parent_id
        )
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/{category_id}/activate", response_model=schemas.Category)
def activate_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> schemas.Category:
    """カテゴリを有効化."""
    try:
        category = crud_category.activate(db, category_id=category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/{category_id}/deactivate", response_model=schemas.Category)
def deactivate_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> schemas.Category:
    """カテゴリを無効化."""
    category = crud_category.deactivate(db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/bulk/sort-order", response_model=list[schemas.Category])
def bulk_update_sort_order(
    *,
    db: Session = Depends(get_db),
    updates: list[dict[str, Any]],
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[schemas.Category]:
    """複数カテゴリの表示順序を一括更新."""
    return crud_category.bulk_update_sort_order(db, updates=updates)


@router.post("/bulk/update", response_model=list[schemas.Category])
def bulk_update_categories(
    *,
    db: Session = Depends(get_db),
    bulk_update: schemas.CategoryBulkUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[schemas.Category]:
    """複数カテゴリを一括更新."""
    updated_categories = []

    for category_id in bulk_update.category_ids:
        category = crud_category.get(db, id=category_id)
        if category:
            try:
                updated_category = crud_category.update(
                    db, db_obj=category, obj_in=bulk_update.updates
                )
                updated_categories.append(updated_category)
            except ValueError:
                # エラーが発生した場合はスキップ
                continue

    return updated_categories


@router.post("/update-counts", response_model=dict[str, int])
def update_all_category_counts(
    *,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, int]:
    """全カテゴリのコンテンツ数を再計算."""
    updated_count = crud_category.update_all_counts(db)
    return {"updated_count": updated_count}


@router.delete("/{category_id}")
def delete_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, str]:
    """カテゴリを削除."""
    category = crud_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # システムカテゴリは削除不可
    if category.is_system:
        raise HTTPException(
            status_code=400, detail="System categories cannot be deleted"
        )

    # 子カテゴリがある場合は削除不可
    if category.has_children:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category with children. "
            "Move or delete children first.",
        )

    # コンテンツがある場合は削除不可
    if category.total_content_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category with content. "
            "Move content to another category first.",
        )

    crud_category.remove(db, id=category_id)
    return {"message": "Category deleted successfully"}
