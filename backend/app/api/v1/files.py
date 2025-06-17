"""File upload and management API endpoints."""

import hashlib
from pathlib import Path
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi import (
    File as UploadedFile,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.crud import file as crud_file
from app.deps import get_current_user, get_db
from app.schemas import file as schemas

router = APIRouter()

# アップロード設定
UPLOAD_DIR = Path("uploads").resolve()
THUMBNAIL_DIR = Path("uploads/thumbnails").resolve()
ALLOWED_EXTENSIONS = {
    "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
    "document": [".pdf", ".doc", ".docx", ".txt", ".md", ".csv", ".xls", ".xlsx"],
    "video": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"],
    "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# ディレクトリ作成
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)


def get_file_hash(file_content: bytes) -> str:
    """ファイルコンテンツからSHA256ハッシュを生成."""
    return hashlib.sha256(file_content).hexdigest()


def validate_file(file: UploadFile) -> tuple[str, str]:
    """ファイルを検証し、ファイルタイプと拡張子を返す."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="ファイル名が必要です")

    # ファイルサイズチェック
    if file.size and file.size > MAX_FILE_SIZE:
        max_size_mb = MAX_FILE_SIZE // (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"ファイルサイズが上限({max_size_mb}MB)を超えています",
        )

    # 拡張子取得
    extension = Path(file.filename).suffix.lower()

    # 許可された拡張子チェック
    allowed = False
    file_type = "other"

    for ftype, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            file_type = ftype
            allowed = True
            break

    if not allowed:
        all_extensions = []
        for exts in ALLOWED_EXTENSIONS.values():
            all_extensions.extend(exts)
        raise HTTPException(
            status_code=400,
            detail="許可されていないファイル形式です。"
            f"許可されている形式: {', '.join(all_extensions)}",
        )

    return file_type, extension.lstrip(".")


async def save_uploaded_file(
    file: UploadFile, file_type: str, extension: str
) -> tuple[str, int, str]:
    """アップロードファイルを保存し、パス、サイズ、ハッシュを返す."""
    # ファイル内容を読み取り
    content = await file.read()
    file_size = len(content)
    file_hash = get_file_hash(content)

    # 保存ファイル名（ハッシュベース）
    filename = f"{file_hash}.{extension}"
    file_path = UPLOAD_DIR / file_type / filename

    # ディレクトリ作成
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # ファイル保存
    file_path.write_bytes(content)

    return str(file_path), file_size, file_hash


@router.get("/", response_model=list[schemas.File])
def get_files(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する件数"),
    file_type: str | None = Query(None, description="ファイルタイプでフィルター"),
    is_public: bool | None = Query(None, description="公開フラグでフィルター"),
    article_id: int | None = Query(None, description="記事IDでフィルター"),
    paper_id: int | None = Query(None, description="論文IDでフィルター"),
    mime_type: str | None = Query(None, description="MIMEタイプでフィルター"),
    extension: str | None = Query(None, description="拡張子でフィルター"),
    min_size: int | None = Query(None, ge=0, description="最小ファイルサイズ"),
    max_size: int | None = Query(None, ge=0, description="最大ファイルサイズ"),
    has_thumbnail: bool | None = Query(None, description="サムネイル有無でフィルター"),
) -> list[schemas.File]:
    """ファイル一覧を取得."""
    filters = {
        "file_type": file_type,
        "is_public": is_public,
        "article_id": article_id,
        "paper_id": paper_id,
        "mime_type": mime_type,
        "extension": extension,
        "min_size": min_size,
        "max_size": max_size,
        "has_thumbnail": has_thumbnail,
    }
    # None値を除去
    filters = {k: v for k, v in filters.items() if v is not None}

    files = crud_file.get_multi_with_filters(
        db, skip=skip, limit=limit, filters=filters
    )

    # URLを追加
    for file_obj in files:
        file_obj.url = file_obj.get_url("/api/v1")
        file_obj.thumbnail_url = file_obj.get_thumbnail_url("/api/v1")

    return files


@router.get("/search", response_model=schemas.FileSearchResult)
def search_files(
    q: str = Query(..., min_length=1, description="検索クエリ"),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する件数"),
) -> schemas.FileSearchResult:
    """ファイルを検索."""
    files = crud_file.search(db, query=q, skip=skip, limit=limit)

    # URLを追加
    for file_obj in files:
        file_obj.url = file_obj.get_url("/api/v1")
        file_obj.thumbnail_url = file_obj.get_thumbnail_url("/api/v1")

    return schemas.FileSearchResult(
        files=files,
        total=len(files),
        page=skip // limit + 1,
        size=limit,
        has_next=len(files) == limit,
    )


@router.get("/stats", response_model=schemas.FileStats)
def get_file_stats(
    db: Session = Depends(get_db),
) -> schemas.FileStats:
    """ファイル統計情報を取得."""
    stats = crud_file.get_stats(db)
    return schemas.FileStats(**stats)


@router.get("/types/{file_type}", response_model=list[schemas.File])
def get_files_by_type(
    file_type: str,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する件数"),
) -> list[schemas.File]:
    """指定タイプのファイルを取得."""
    files = crud_file.get_by_type(db, file_type=file_type, skip=skip, limit=limit)

    # URLを追加
    for file_obj in files:
        file_obj.url = file_obj.get_url("/api/v1")
        file_obj.thumbnail_url = file_obj.get_thumbnail_url("/api/v1")

    return files


@router.get("/images", response_model=list[schemas.File])
def get_images(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する件数"),
) -> list[schemas.File]:
    """画像ファイルを取得."""
    images = crud_file.get_images(db, skip=skip, limit=limit)

    # URLを追加
    for file_obj in images:
        file_obj.url = file_obj.get_url("/api/v1")
        file_obj.thumbnail_url = file_obj.get_thumbnail_url("/api/v1")

    return images


@router.get("/documents", response_model=list[schemas.File])
def get_documents(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する件数"),
) -> list[schemas.File]:
    """ドキュメントファイルを取得."""
    documents = crud_file.get_documents(db, skip=skip, limit=limit)

    # URLを追加
    for file_obj in documents:
        file_obj.url = file_obj.get_url("/api/v1")
        file_obj.thumbnail_url = file_obj.get_thumbnail_url("/api/v1")

    return documents


@router.get("/orphaned", response_model=list[schemas.File])
def get_orphaned_files(
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[schemas.File]:
    """孤立ファイルを取得."""
    files = crud_file.get_orphaned_files(db)

    # URLを追加
    for file_obj in files:
        file_obj.url = file_obj.get_url("/api/v1")
        file_obj.thumbnail_url = file_obj.get_thumbnail_url("/api/v1")

    return files


@router.get("/popular", response_model=list[schemas.File])
def get_popular_files(
    db: Session = Depends(get_db),
    min_downloads: int = Query(1, ge=0, description="最小ダウンロード数"),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する件数"),
) -> list[schemas.File]:
    """人気ファイルを取得."""
    files = crud_file.get_popular_files(
        db, min_downloads=min_downloads, skip=skip, limit=limit
    )

    # URLを追加
    for file_obj in files:
        file_obj.url = file_obj.get_url("/api/v1")
        file_obj.thumbnail_url = file_obj.get_thumbnail_url("/api/v1")

    return files


@router.get("/{file_id}", response_model=schemas.File)
def get_file(
    file_id: int,
    db: Session = Depends(get_db),
) -> schemas.File:
    """指定されたIDのファイルを取得."""
    file_obj = crud_file.get(db, id=file_id)
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")

    # URLを追加
    file_obj.url = file_obj.get_url("/api/v1")
    file_obj.thumbnail_url = file_obj.get_thumbnail_url("/api/v1")

    return file_obj


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
) -> FileResponse:
    """ファイルをダウンロード."""
    file_obj = crud_file.get(db, id=file_id)
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")

    # 公開フラグチェック（必要に応じて認証チェックも追加）
    if not file_obj.is_public:
        raise HTTPException(status_code=403, detail="File is not public")

    # ファイル存在チェック
    if not Path(file_obj.file_path).exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    # ダウンロード数をインクリメント
    crud_file.increment_download_count(db, file_id=file_id)

    return FileResponse(
        path=file_obj.file_path,
        filename=file_obj.original_filename,
        media_type=file_obj.mime_type,
    )


@router.get("/{file_id}/thumbnail")
def get_thumbnail(
    file_id: int,
    db: Session = Depends(get_db),
) -> FileResponse:
    """サムネイルを取得."""
    file_obj = crud_file.get(db, id=file_id)
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")

    if not file_obj.has_thumbnail or not file_obj.thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    # サムネイルファイル存在チェック
    if not Path(file_obj.thumbnail_path).exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found on disk")

    return FileResponse(
        path=file_obj.thumbnail_path,
        media_type="image/jpeg",  # サムネイルは通常JPEG
    )


@router.post("/upload", response_model=schemas.FileUploadResponse)
async def upload_file(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = UploadedFile(...),
    description: str | None = Form(None),
    alt_text: str | None = Form(None),
    is_public: bool = Form(True),
    article_id: int | None = Form(None),
    paper_id: int | None = Form(None),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> schemas.FileUploadResponse:
    """ファイルをアップロード."""
    # ファイル検証
    file_type, extension = validate_file(file)

    # 重複チェック用にハッシュを先に計算
    content = await file.read()
    file_hash = get_file_hash(content)

    # ハッシュによる重複チェック
    existing_file = crud_file.get_by_hash(db, file_hash=file_hash)
    if existing_file:
        # 既存ファイルのURLを追加
        existing_file.url = existing_file.get_url("/api/v1")
        existing_file.thumbnail_url = existing_file.get_thumbnail_url("/api/v1")

        return schemas.FileUploadResponse(
            file_id=existing_file.id,
            filename=existing_file.filename,
            file_size=existing_file.file_size,
            file_size_readable=existing_file.file_size_readable,
            mime_type=existing_file.mime_type,
            file_type=existing_file.file_type,
            url=existing_file.url,
            thumbnail_url=existing_file.thumbnail_url,
            is_image=existing_file.is_image,
            width=existing_file.width,
            height=existing_file.height,
        )

    # ファイルを保存
    file.file.seek(0)  # ファイルポインタをリセット
    file_path, file_size, _ = await save_uploaded_file(file, file_type, extension)

    # MIMEタイプ決定
    mime_type = file.content_type or "application/octet-stream"

    # 画像の場合は寸法を取得（実装は簡略化）
    width, height = None, None
    if file_type == "image":
        try:
            from PIL import Image

            with Image.open(file_path) as img:
                width, height = img.size
        except ImportError:
            # PIL が利用できない場合はスキップ
            pass
        except Exception:  # nosec B110
            # 画像読み込みエラーの場合はスキップ
            pass

    # ファイル情報をDBに保存
    file_create = schemas.FileCreate(
        filename=file.filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=mime_type,
        file_extension=extension,
        file_hash=file_hash,
        file_type=file_type,
        description=description,
        alt_text=alt_text,
        is_public=is_public,
        article_id=article_id,
        paper_id=paper_id,
        width=width,
        height=height,
    )

    db_file = crud_file.create(db, obj_in=file_create)

    # URLを生成
    url = db_file.get_url("/api/v1")
    thumbnail_url = db_file.get_thumbnail_url("/api/v1")

    return schemas.FileUploadResponse(
        file_id=db_file.id,
        filename=db_file.filename,
        file_size=db_file.file_size,
        file_size_readable=db_file.file_size_readable,
        mime_type=db_file.mime_type,
        file_type=db_file.file_type,
        url=url,
        thumbnail_url=thumbnail_url,
        is_image=db_file.is_image,
        width=db_file.width,
        height=db_file.height,
    )


@router.post("/upload/bulk", response_model=schemas.FileBulkUploadResponse)
async def upload_multiple_files(
    *,
    db: Session = Depends(get_db),
    files: list[UploadFile] = UploadedFile(...),
    is_public: bool = Form(True),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> schemas.FileBulkUploadResponse:
    """複数ファイルを一括アップロード."""
    uploaded_files = []
    failed_files = []

    for file in files:
        try:
            # 個別ファイルのアップロード処理
            file_type, extension = validate_file(file)

            content = await file.read()
            file_hash = get_file_hash(content)

            # 重複チェック
            existing_file = crud_file.get_by_hash(db, file_hash=file_hash)
            if existing_file:
                existing_file.url = existing_file.get_url("/api/v1")
                existing_file.thumbnail_url = existing_file.get_thumbnail_url("/api/v1")

                uploaded_files.append(
                    schemas.FileUploadResponse(
                        file_id=existing_file.id,
                        filename=existing_file.filename,
                        file_size=existing_file.file_size,
                        file_size_readable=existing_file.file_size_readable,
                        mime_type=existing_file.mime_type,
                        file_type=existing_file.file_type,
                        url=existing_file.url,
                        thumbnail_url=existing_file.thumbnail_url,
                        is_image=existing_file.is_image,
                        width=existing_file.width,
                        height=existing_file.height,
                    )
                )
                continue

            # ファイル保存
            file.file.seek(0)
            file_path, file_size, _ = await save_uploaded_file(
                file, file_type, extension
            )

            # MIMEタイプ
            mime_type = file.content_type or "application/octet-stream"

            # DB保存
            file_create = schemas.FileCreate(
                filename=file.filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type,
                file_extension=extension,
                file_hash=file_hash,
                file_type=file_type,
                is_public=is_public,
            )

            db_file = crud_file.create(db, obj_in=file_create)

            uploaded_files.append(
                schemas.FileUploadResponse(
                    file_id=db_file.id,
                    filename=db_file.filename,
                    file_size=db_file.file_size,
                    file_size_readable=db_file.file_size_readable,
                    mime_type=db_file.mime_type,
                    file_type=db_file.file_type,
                    url=db_file.get_url("/api/v1"),
                    thumbnail_url=db_file.get_thumbnail_url("/api/v1"),
                    is_image=db_file.is_image,
                    width=db_file.width,
                    height=db_file.height,
                )
            )

        except Exception as e:
            failed_files.append(
                {
                    "filename": file.filename,
                    "error": str(e),
                }
            )

    return schemas.FileBulkUploadResponse(
        uploaded_files=uploaded_files,
        failed_files=failed_files,
        total_files=len(files),
        success_count=len(uploaded_files),
        failure_count=len(failed_files),
    )


@router.put("/{file_id}", response_model=schemas.File)
def update_file(
    *,
    db: Session = Depends(get_db),
    file_id: int,
    file_in: schemas.FileUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> schemas.File:
    """ファイル情報を更新."""
    file_obj = crud_file.get(db, id=file_id)
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")

    updated_file = crud_file.update(db, db_obj=file_obj, obj_in=file_in)

    # URLを追加
    updated_file.url = updated_file.get_url("/api/v1")
    updated_file.thumbnail_url = updated_file.get_thumbnail_url("/api/v1")

    return updated_file


@router.post("/{file_id}/associate/article/{article_id}", response_model=schemas.File)
def associate_file_with_article(
    *,
    db: Session = Depends(get_db),
    file_id: int,
    article_id: int,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> schemas.File:
    """ファイルを記事に関連付け."""
    file_obj = crud_file.associate_with_article(
        db, file_id=file_id, article_id=article_id
    )
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")

    # URLを追加
    file_obj.url = file_obj.get_url("/api/v1")
    file_obj.thumbnail_url = file_obj.get_thumbnail_url("/api/v1")

    return file_obj


@router.post("/{file_id}/associate/paper/{paper_id}", response_model=schemas.File)
def associate_file_with_paper(
    *,
    db: Session = Depends(get_db),
    file_id: int,
    paper_id: int,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> schemas.File:
    """ファイルを論文に関連付け."""
    file_obj = crud_file.associate_with_paper(db, file_id=file_id, paper_id=paper_id)
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")

    # URLを追加
    file_obj.url = file_obj.get_url("/api/v1")
    file_obj.thumbnail_url = file_obj.get_thumbnail_url("/api/v1")

    return file_obj


@router.delete("/{file_id}/associations")
def remove_file_associations(
    *,
    db: Session = Depends(get_db),
    file_id: int,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, str]:
    """ファイルの関連付けを解除."""
    file_obj = crud_file.remove_associations(db, file_id=file_id)
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")

    return {"message": "File associations removed successfully"}


@router.post("/bulk/visibility", response_model=list[schemas.File])
def bulk_update_file_visibility(
    *,
    db: Session = Depends(get_db),
    file_ids: list[int],
    is_public: bool,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[schemas.File]:
    """複数ファイルの公開設定を一括更新."""
    files = crud_file.bulk_update_visibility(db, file_ids=file_ids, is_public=is_public)

    # URLを追加
    for file_obj in files:
        file_obj.url = file_obj.get_url("/api/v1")
        file_obj.thumbnail_url = file_obj.get_thumbnail_url("/api/v1")

    return files


@router.delete("/cleanup/orphaned")
def cleanup_orphaned_files(
    *,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, int]:
    """孤立ファイルを削除."""
    deleted_count = crud_file.cleanup_orphaned_files(db)
    return {"deleted_count": deleted_count}


@router.delete("/{file_id}")
def delete_file(
    *,
    db: Session = Depends(get_db),
    file_id: int,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, str]:
    """ファイルを削除."""
    file_obj = crud_file.get(db, id=file_id)
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")

    # ファイルシステムからも削除
    try:
        file_path = Path(file_obj.file_path)
        if file_path.exists():
            file_path.unlink()
        if file_obj.thumbnail_path:
            thumbnail_path = Path(file_obj.thumbnail_path)
            if thumbnail_path.exists():
                thumbnail_path.unlink()
    except OSError:
        # ファイル削除エラーは無視（DBからは削除）
        pass

    crud_file.remove(db, id=file_id)
    return {"message": "File deleted successfully"}
