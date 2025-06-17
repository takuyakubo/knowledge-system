"""Paper API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.deps import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.Paper])
def read_papers(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit items"),
    category_id: int | None = Query(None, description="Filter by category"),
    reading_status: str | None = Query(None, description="Filter by reading status"),
    paper_type: str | None = Query(None, description="Filter by paper type"),
    is_favorite: bool | None = Query(None, description="Filter by favorite status"),
    min_priority: int | None = Query(None, ge=1, le=5, description="Minimum priority"),
    publication_year: int | None = Query(
        None, description="Filter by publication year"
    ),
    search: str | None = Query(None, description="Search query"),
) -> Any:
    """論文一覧を取得."""
    if search:
        papers = crud.paper.search(db, query=search, skip=skip, limit=limit)
    else:
        filters = {
            "category_id": category_id,
            "reading_status": reading_status,
            "paper_type": paper_type,
            "is_favorite": is_favorite,
            "min_priority": min_priority,
            "publication_year": publication_year,
        }
        papers = crud.paper.get_multi_with_filters(
            db, skip=skip, limit=limit, filters=filters
        )
    return papers


@router.post("/", response_model=schemas.Paper)
def create_paper(
    *,
    db: Session = Depends(get_db),
    paper_in: schemas.PaperCreate,
) -> Any:
    """新しい論文を作成."""
    # DOI、arXiv ID、PMID の重複チェック
    if paper_in.doi:
        existing_paper = crud.paper.get_by_doi(db, doi=paper_in.doi)
        if existing_paper:
            raise HTTPException(
                status_code=400,
                detail=f"Paper with DOI {paper_in.doi} already exists",
            )

    if paper_in.arxiv_id:
        existing_paper = crud.paper.get_by_arxiv_id(db, arxiv_id=paper_in.arxiv_id)
        if existing_paper:
            raise HTTPException(
                status_code=400,
                detail=f"Paper with arXiv ID {paper_in.arxiv_id} already exists",
            )

    if paper_in.pmid:
        existing_paper = crud.paper.get_by_pmid(db, pmid=paper_in.pmid)
        if existing_paper:
            raise HTTPException(
                status_code=400,
                detail=f"Paper with PMID {paper_in.pmid} already exists",
            )

    tag_ids = paper_in.tag_ids if hasattr(paper_in, "tag_ids") else []
    paper = crud.paper.create_with_tags(db, obj_in=paper_in, tag_ids=tag_ids)
    return paper


@router.get("/favorites", response_model=list[schemas.Paper])
def read_favorite_papers(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit items"),
) -> Any:
    """お気に入り論文を取得."""
    papers = crud.paper.get_favorites(db, skip=skip, limit=limit)
    return papers


@router.get("/status/{reading_status}", response_model=list[schemas.Paper])
def read_papers_by_status(
    reading_status: str,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit items"),
) -> Any:
    """読書ステータス別に論文を取得."""
    valid_statuses = ["to_read", "reading", "completed", "skipped"]
    if reading_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid reading status. Must be one of {valid_statuses}",
        )

    papers = crud.paper.get_by_reading_status(
        db, reading_status=reading_status, skip=skip, limit=limit
    )
    return papers


@router.get("/year/{year}", response_model=list[schemas.Paper])
def read_papers_by_year(
    year: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit items"),
) -> Any:
    """発行年別に論文を取得."""
    papers = crud.paper.get_by_year(db, year=year, skip=skip, limit=limit)
    return papers


@router.get("/high-priority", response_model=list[schemas.Paper])
def read_high_priority_papers(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit items"),
    min_priority: int = Query(4, ge=1, le=5, description="Minimum priority"),
) -> Any:
    """高優先度論文を取得."""
    papers = crud.paper.get_by_priority(
        db, min_priority=min_priority, skip=skip, limit=limit
    )
    return papers


@router.get("/{paper_id}", response_model=schemas.Paper)
def read_paper(
    *,
    db: Session = Depends(get_db),
    paper_id: int,
) -> Any:
    """論文詳細を取得."""
    paper = crud.paper.get(db, id=paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.get("/doi/{doi:path}", response_model=schemas.Paper)
def read_paper_by_doi(
    *,
    db: Session = Depends(get_db),
    doi: str,
) -> Any:
    """DOIで論文を取得."""
    paper = crud.paper.get_by_doi(db, doi=doi)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.get("/arxiv/{arxiv_id}", response_model=schemas.Paper)
def read_paper_by_arxiv(
    *,
    db: Session = Depends(get_db),
    arxiv_id: str,
) -> Any:
    """arXiv IDで論文を取得."""
    paper = crud.paper.get_by_arxiv_id(db, arxiv_id=arxiv_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.put("/{paper_id}", response_model=schemas.Paper)
def update_paper(
    *,
    db: Session = Depends(get_db),
    paper_id: int,
    paper_in: schemas.PaperUpdate,
) -> Any:
    """論文を更新."""
    paper = crud.paper.get(db, id=paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    paper = crud.paper.update_with_tags(db, db_obj=paper, obj_in=paper_in)
    return paper


@router.post("/{paper_id}/rating", response_model=schemas.Paper)
def rate_paper(
    *,
    db: Session = Depends(get_db),
    paper_id: int,
    rating_in: schemas.PaperRating,
) -> Any:
    """論文を評価."""
    paper = crud.paper.get(db, id=paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    try:
        paper = crud.paper.set_rating(db, db_obj=paper, rating=rating_in.rating)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return paper


@router.post("/{paper_id}/status", response_model=schemas.Paper)
def update_reading_status(
    *,
    db: Session = Depends(get_db),
    paper_id: int,
    status_in: schemas.PaperStatus,
) -> Any:
    """読書ステータスを更新."""
    paper = crud.paper.get(db, id=paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    try:
        paper = crud.paper.set_reading_status(
            db, db_obj=paper, status=status_in.reading_status
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return paper


@router.post("/{paper_id}/favorite", response_model=schemas.Paper)
def toggle_paper_favorite(
    *,
    db: Session = Depends(get_db),
    paper_id: int,
) -> Any:
    """お気に入り状態を切り替え."""
    paper = crud.paper.get(db, id=paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    paper = crud.paper.toggle_favorite(db, db_obj=paper)
    return paper


@router.post("/{paper_id}/cite", response_model=schemas.Paper)
def increment_citation(
    *,
    db: Session = Depends(get_db),
    paper_id: int,
) -> Any:
    """被引用数を増加."""
    paper = crud.paper.get(db, id=paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    paper = crud.paper.increment_citation_count(db, db_obj=paper)
    return paper


@router.delete("/{paper_id}", response_model=schemas.Paper)
def delete_paper(
    *,
    db: Session = Depends(get_db),
    paper_id: int,
) -> Any:
    """論文を削除."""
    paper = crud.paper.get(db, id=paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    paper = crud.paper.remove(db, id=paper_id)
    return paper
