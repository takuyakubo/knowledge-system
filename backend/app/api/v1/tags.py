"""Tag API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.deps import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.Tag])
def read_tags(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit items"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    is_system: bool | None = Query(None, description="Filter by system status"),
    min_usage: int | None = Query(None, ge=0, description="Minimum usage count"),
    color: str | None = Query(None, description="Filter by color"),
    search: str | None = Query(None, description="Search query"),
) -> Any:
    """タグ一覧を取得."""
    if search:
        tags = crud.tag.search(db, query=search, skip=skip, limit=limit)
    else:
        filters = {
            "is_active": is_active,
            "is_system": is_system,
            "min_usage": min_usage,
            "color": color,
        }
        tags = crud.tag.get_multi_with_filters(
            db, skip=skip, limit=limit, filters=filters
        )
    return tags


@router.post("/", response_model=schemas.Tag)
def create_tag(
    *,
    db: Session = Depends(get_db),
    tag_in: schemas.TagCreate,
) -> Any:
    """新しいタグを作成."""
    # 重複チェック
    existing_tag = crud.tag.get_by_name(db, name=tag_in.name)
    if existing_tag:
        raise HTTPException(
            status_code=400,
            detail=f"Tag with name '{tag_in.name}' already exists",
        )

    tag = crud.tag.create_with_slug(db, obj_in=tag_in)
    return tag


@router.post("/bulk", response_model=list[schemas.Tag])
def create_tags_bulk(
    *,
    db: Session = Depends(get_db),
    bulk_data: schemas.TagBulkCreate,
) -> Any:
    """タグ名のリストから一括作成."""
    tags = crud.tag.bulk_create_from_names(db, tag_names=bulk_data.tag_names)
    return tags


@router.get("/active", response_model=list[schemas.Tag])
def read_active_tags(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit items"),
) -> Any:
    """有効なタグを取得."""
    tags = crud.tag.get_active_tags(db, skip=skip, limit=limit)
    return tags


@router.get("/popular", response_model=list[schemas.Tag])
def read_popular_tags(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="Limit items"),
    min_usage: int = Query(1, ge=0, description="Minimum usage count"),
) -> Any:
    """人気タグを取得."""
    tags = crud.tag.get_popular_tags(db, limit=limit, min_usage=min_usage)
    return tags


@router.get("/system", response_model=list[schemas.Tag])
def read_system_tags(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit items"),
) -> Any:
    """システムタグを取得."""
    tags = crud.tag.get_system_tags(db, skip=skip, limit=limit)
    return tags


@router.get("/unused", response_model=list[schemas.Tag])
def read_unused_tags(
    db: Session = Depends(get_db),
) -> Any:
    """使用されていないタグを取得."""
    tags = crud.tag.get_unused_tags(db)
    return tags


@router.get("/stats", response_model=list[schemas.TagUsageStats])
def read_tag_stats(
    db: Session = Depends(get_db),
) -> Any:
    """タグの使用統計を取得."""
    stats = crud.tag.get_usage_stats(db)
    return stats


@router.get("/{tag_id}", response_model=schemas.Tag)
def read_tag(
    *,
    db: Session = Depends(get_db),
    tag_id: int,
) -> Any:
    """タグ詳細を取得."""
    tag = crud.tag.get(db, id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.get("/slug/{slug}", response_model=schemas.Tag)
def read_tag_by_slug(
    *,
    db: Session = Depends(get_db),
    slug: str,
) -> Any:
    """スラッグでタグを取得."""
    tag = crud.tag.get_by_slug(db, slug=slug)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.put("/{tag_id}", response_model=schemas.Tag)
def update_tag(
    *,
    db: Session = Depends(get_db),
    tag_id: int,
    tag_in: schemas.TagUpdate,
) -> Any:
    """タグを更新."""
    tag = crud.tag.get(db, id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # 名前の重複チェック（自分以外）
    if tag_in.name and tag_in.name != tag.name:
        existing_tag = crud.tag.get_by_name(db, name=tag_in.name)
        if existing_tag and existing_tag.id != tag_id:
            raise HTTPException(
                status_code=400,
                detail=f"Tag with name '{tag_in.name}' already exists",
            )

    tag = crud.tag.update(db, db_obj=tag, obj_in=tag_in)
    return tag


@router.post("/{tag_id}/activate", response_model=schemas.Tag)
def activate_tag(
    *,
    db: Session = Depends(get_db),
    tag_id: int,
) -> Any:
    """タグを有効化."""
    tag = crud.tag.activate(db, tag_id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.post("/{tag_id}/deactivate", response_model=schemas.Tag)
def deactivate_tag(
    *,
    db: Session = Depends(get_db),
    tag_id: int,
) -> Any:
    """タグを無効化."""
    tag = crud.tag.deactivate(db, tag_id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.post("/{tag_id}/increment-usage", response_model=schemas.Tag)
def increment_tag_usage(
    *,
    db: Session = Depends(get_db),
    tag_id: int,
) -> Any:
    """タグの使用回数を増加."""
    tag = crud.tag.increment_usage(db, tag_id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.post("/merge", response_model=schemas.Tag)
def merge_tags(
    *,
    db: Session = Depends(get_db),
    merge_data: schemas.TagMerge,
) -> Any:
    """複数のタグを1つに統合."""
    # ターゲットタグの存在確認
    target_tag = crud.tag.get(db, id=merge_data.target_tag_id)
    if not target_tag:
        raise HTTPException(status_code=404, detail="Target tag not found")

    # ソースタグの存在確認
    for source_id in merge_data.source_tag_ids:
        source_tag = crud.tag.get(db, id=source_id)
        if not source_tag:
            raise HTTPException(
                status_code=404, detail=f"Source tag {source_id} not found"
            )

    tag = crud.tag.merge_tags(
        db,
        source_ids=merge_data.source_tag_ids,
        target_id=merge_data.target_tag_id,
    )
    return tag


@router.post("/update-usage-counts", response_model=dict[str, int])
def update_usage_counts(
    db: Session = Depends(get_db),
) -> Any:
    """全タグの使用回数を再計算."""
    updated_count = crud.tag.update_usage_counts(db)
    return {"updated_count": updated_count}


@router.delete("/{tag_id}", response_model=schemas.Tag)
def delete_tag(
    *,
    db: Session = Depends(get_db),
    tag_id: int,
) -> Any:
    """タグを削除."""
    tag = crud.tag.get(db, id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # システムタグの削除を防ぐ
    if tag.is_system:
        raise HTTPException(status_code=400, detail="Cannot delete system tags")

    tag = crud.tag.remove(db, id=tag_id)
    return tag
