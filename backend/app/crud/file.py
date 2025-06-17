"""CRUD operations for File model."""

from typing import Any

from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.file import File
from app.schemas.file import FileCreate, FileUpdate


class CRUDFile(CRUDBase[File, FileCreate, FileUpdate]):
    """File CRUD operations."""

    def get_by_hash(self, db: Session, *, file_hash: str) -> File | None:
        """ファイルハッシュでファイルを取得."""
        return db.query(File).filter(File.file_hash == file_hash).first()

    def get_by_filename(self, db: Session, *, filename: str) -> list[File]:
        """ファイル名でファイルを検索."""
        return (
            db.query(File)
            .filter(File.filename.ilike(f"%{filename}%"))
            .order_by(desc(File.created_at))
            .all()
        )

    def get_by_article_id(self, db: Session, *, article_id: int) -> list[File]:
        """記事IDでファイルを取得."""
        return (
            db.query(File)
            .filter(File.article_id == article_id)
            .order_by(desc(File.created_at))
            .all()
        )

    def get_by_paper_id(self, db: Session, *, paper_id: int) -> list[File]:
        """論文IDでファイルを取得."""
        return (
            db.query(File)
            .filter(File.paper_id == paper_id)
            .order_by(desc(File.created_at))
            .all()
        )

    def get_by_type(
        self, db: Session, *, file_type: str, skip: int = 0, limit: int = 100
    ) -> list[File]:
        """ファイルタイプでファイルを取得."""
        return (
            db.query(File)
            .filter(File.file_type == file_type)
            .order_by(desc(File.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_images(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[File]:
        """画像ファイルを取得."""
        return (
            db.query(File)
            .filter(File.file_type == "image")
            .order_by(desc(File.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_documents(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[File]:
        """ドキュメントファイルを取得."""
        return (
            db.query(File)
            .filter(File.file_type.in_(["document", "pdf"]))
            .order_by(desc(File.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_public_files(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[File]:
        """公開ファイルを取得."""
        return (
            db.query(File)
            .filter(File.is_public.is_(True))
            .order_by(desc(File.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_orphaned_files(self, db: Session) -> list[File]:
        """孤立ファイル（記事・論文に関連付けされていない）を取得."""
        return (
            db.query(File)
            .filter(File.article_id.is_(None), File.paper_id.is_(None))
            .order_by(desc(File.created_at))
            .all()
        )

    def get_large_files(
        self, db: Session, *, min_size_mb: float = 10.0, skip: int = 0, limit: int = 100
    ) -> list[File]:
        """大きなファイルを取得."""
        min_size_bytes = int(min_size_mb * 1024 * 1024)
        return (
            db.query(File)
            .filter(File.file_size >= min_size_bytes)
            .order_by(desc(File.file_size))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_popular_files(
        self, db: Session, *, min_downloads: int = 1, skip: int = 0, limit: int = 100
    ) -> list[File]:
        """人気ファイルを取得（ダウンロード数順）."""
        return (
            db.query(File)
            .filter(File.download_count >= min_downloads)
            .order_by(desc(File.download_count), desc(File.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> list[File]:
        """ファイルを検索."""
        search_filter = or_(
            File.filename.ilike(f"%{query}%"),
            File.original_filename.ilike(f"%{query}%"),
            File.description.ilike(f"%{query}%"),
            File.mime_type.ilike(f"%{query}%"),
        )

        return (
            db.query(File)
            .filter(search_filter)
            .order_by(desc(File.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def increment_download_count(self, db: Session, *, file_id: int) -> File | None:
        """ダウンロード数をインクリメント."""
        file_obj = self.get(db, id=file_id)
        if file_obj:
            file_obj.increment_download_count()
            db.add(file_obj)
            db.commit()
            db.refresh(file_obj)
        return file_obj

    def get_stats(self, db: Session) -> dict[str, Any]:
        """ファイル統計情報を取得."""
        total_files = db.query(func.count(File.id)).scalar() or 0
        total_size = db.query(func.sum(File.file_size)).scalar() or 0

        # ファイルタイプ別集計
        type_stats = (
            db.query(File.file_type, func.count(File.id)).group_by(File.file_type).all()
        )
        by_type = {file_type: count for file_type, count in type_stats}

        # 拡張子別集計
        extension_stats = (
            db.query(File.file_extension, func.count(File.id))
            .group_by(File.file_extension)
            .all()
        )
        by_extension = {ext: count for ext, count in extension_stats}

        # 平均サイズ（MB）
        average_size = 0.0
        if total_files > 0:
            average_size = round((total_size / total_files) / (1024 * 1024), 2)

        # 最大ファイル
        largest_file = db.query(File).order_by(desc(File.file_size)).first()

        largest_file_info = None
        if largest_file:
            largest_file_info = {
                "id": largest_file.id,
                "filename": largest_file.filename,
                "size": largest_file.file_size,
                "size_readable": largest_file.file_size_readable,
                "type": largest_file.file_type,
            }

        return {
            "total_files": total_files,
            "total_size": total_size,
            "total_size_readable": self._bytes_to_readable(total_size),
            "by_type": by_type,
            "by_extension": by_extension,
            "average_size": average_size,
            "largest_file": largest_file_info,
        }

    def cleanup_orphaned_files(self, db: Session) -> int:
        """孤立ファイルを削除."""
        orphaned_files = self.get_orphaned_files(db)
        deleted_count = 0

        for file_obj in orphaned_files:
            # ファイルシステムからも削除する場合は、ここでfile_pathを使って削除
            # import os
            # try:
            #     os.remove(file_obj.file_path)
            #     if file_obj.thumbnail_path:
            #         os.remove(file_obj.thumbnail_path)
            # except OSError:
            #     pass

            db.delete(file_obj)
            deleted_count += 1

        db.commit()
        return deleted_count

    def bulk_update_visibility(
        self, db: Session, *, file_ids: list[int], is_public: bool
    ) -> list[File]:
        """複数ファイルの公開設定を一括更新."""
        files = db.query(File).filter(File.id.in_(file_ids)).all()

        for file_obj in files:
            file_obj.is_public = is_public
            db.add(file_obj)

        db.commit()

        for file_obj in files:
            db.refresh(file_obj)

        return files

    def associate_with_article(
        self, db: Session, *, file_id: int, article_id: int
    ) -> File | None:
        """ファイルを記事に関連付け."""
        file_obj = self.get(db, id=file_id)
        if file_obj:
            file_obj.article_id = article_id
            file_obj.paper_id = None  # 論文との関連付けは解除
            db.add(file_obj)
            db.commit()
            db.refresh(file_obj)
        return file_obj

    def associate_with_paper(
        self, db: Session, *, file_id: int, paper_id: int
    ) -> File | None:
        """ファイルを論文に関連付け."""
        file_obj = self.get(db, id=file_id)
        if file_obj:
            file_obj.paper_id = paper_id
            file_obj.article_id = None  # 記事との関連付けは解除
            db.add(file_obj)
            db.commit()
            db.refresh(file_obj)
        return file_obj

    def remove_associations(self, db: Session, *, file_id: int) -> File | None:
        """ファイルの関連付けを全て解除."""
        file_obj = self.get(db, id=file_id)
        if file_obj:
            file_obj.article_id = None
            file_obj.paper_id = None
            db.add(file_obj)
            db.commit()
            db.refresh(file_obj)
        return file_obj

    def get_multi_with_filters(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[File]:
        """複数フィルターでファイルを取得."""
        query = db.query(File)

        if filters:
            if filters.get("file_type") is not None:
                query = query.filter(File.file_type == filters["file_type"])
            if filters.get("is_public") is not None:
                query = query.filter(File.is_public.is_(filters["is_public"]))
            if filters.get("article_id") is not None:
                query = query.filter(File.article_id == filters["article_id"])
            if filters.get("paper_id") is not None:
                query = query.filter(File.paper_id == filters["paper_id"])
            if filters.get("mime_type") is not None:
                query = query.filter(File.mime_type == filters["mime_type"])
            if filters.get("min_size") is not None:
                query = query.filter(File.file_size >= filters["min_size"])
            if filters.get("max_size") is not None:
                query = query.filter(File.file_size <= filters["max_size"])
            if filters.get("has_thumbnail") is not None:
                query = query.filter(File.has_thumbnail.is_(filters["has_thumbnail"]))
            if filters.get("extension") is not None:
                query = query.filter(File.file_extension == filters["extension"])

        return query.order_by(desc(File.created_at)).offset(skip).limit(limit).all()

    def _bytes_to_readable(self, size: int) -> str:
        """バイト数を人間が読みやすい形式に変換."""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{round(size / 1024, 1)} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{round(size / (1024 * 1024), 1)} MB"
        else:
            return f"{round(size / (1024 * 1024 * 1024), 1)} GB"


file = CRUDFile(File)
