"""File model for managing uploaded files and attachments."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.paper import Paper


class File(Base, TimestampMixin):
    """アップロードファイルを管理するモデル."""

    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True, doc="ファイルID")

    # 基本情報
    filename: Mapped[str] = mapped_column(
        String(255), nullable=False, doc="元のファイル名"
    )
    original_filename: Mapped[str] = mapped_column(
        String(255), nullable=False, doc="アップロード時の元ファイル名"
    )
    file_path: Mapped[str] = mapped_column(
        String(500), nullable=False, doc="サーバー上のファイルパス"
    )

    # ファイル属性
    file_size: Mapped[int] = mapped_column(
        Integer, nullable=False, doc="ファイルサイズ(バイト)"
    )
    mime_type: Mapped[str] = mapped_column(
        String(100), nullable=False, doc="MIMEタイプ"
    )
    file_extension: Mapped[str] = mapped_column(
        String(10), nullable=False, doc="ファイル拡張子"
    )

    # ハッシュ・チェックサム
    file_hash: Mapped[str | None] = mapped_column(
        String(64), unique=True, nullable=True, doc="ファイルのSHA256ハッシュ"
    )

    # メタデータ
    description: Mapped[str | None] = mapped_column(
        String(500), nullable=True, doc="ファイルの説明"
    )
    alt_text: Mapped[str | None] = mapped_column(
        String(255), nullable=True, doc="画像の代替テキスト"
    )

    # 分類・関連付け
    file_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="ファイル種別 (image, document, pdf, video, audio, other)",
    )

    # 関連エンティティ
    article_id: Mapped[int | None] = mapped_column(
        ForeignKey("articles.id"), nullable=True, index=True, doc="関連記事ID"
    )
    paper_id: Mapped[int | None] = mapped_column(
        ForeignKey("papers.id"), nullable=True, index=True, doc="関連論文ID"
    )

    # アクセス制御
    is_public: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, doc="公開フラグ"
    )

    # 画像固有の属性（画像ファイルの場合）
    width: Mapped[int | None] = mapped_column(
        Integer, nullable=True, doc="画像の幅(ピクセル)"
    )
    height: Mapped[int | None] = mapped_column(
        Integer, nullable=True, doc="画像の高さ(ピクセル)"
    )

    # 統計
    download_count: Mapped[int] = mapped_column(
        default=0, nullable=False, doc="ダウンロード数"
    )

    # サムネイル関連
    has_thumbnail: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, doc="サムネイルの有無"
    )
    thumbnail_path: Mapped[str | None] = mapped_column(
        String(500), nullable=True, doc="サムネイルファイルパス"
    )

    # リレーション
    article: Mapped["Article | None"] = relationship("Article", back_populates="files")
    paper: Mapped["Paper | None"] = relationship("Paper", back_populates="files")

    def __repr__(self) -> str:
        """デバッグ用の文字列表現."""
        return (
            f"<File(id={self.id}, filename='{self.filename}', type='{self.file_type}')>"
        )

    @property
    def file_size_mb(self) -> float:
        """ファイルサイズをMB単位で取得."""
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def file_size_readable(self) -> str:
        """人間が読みやすい形式でファイルサイズを取得."""
        size = self.file_size

        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{round(size / 1024, 1)} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{round(size / (1024 * 1024), 1)} MB"
        else:
            return f"{round(size / (1024 * 1024 * 1024), 1)} GB"

    @property
    def is_image(self) -> bool:
        """画像ファイルかどうか."""
        return self.file_type == "image" or self.mime_type.startswith("image/")

    @property
    def is_pdf(self) -> bool:
        """PDFファイルかどうか."""
        return self.file_type == "pdf" or self.mime_type == "application/pdf"

    @property
    def is_document(self) -> bool:
        """ドキュメントファイルかどうか."""
        document_mimes = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "text/plain",
            "text/markdown",
        ]
        return self.file_type == "document" or self.mime_type in document_mimes

    def increment_download_count(self) -> None:
        """ダウンロード数をインクリメント."""
        self.download_count += 1

    def get_url(self, base_url: str = "") -> str:
        """ファイルのアクセスURLを生成."""
        return f"{base_url.rstrip('/')}/files/{self.id}/download"

    def get_thumbnail_url(self, base_url: str = "") -> str | None:
        """サムネイルのアクセスURLを生成."""
        if not self.has_thumbnail:
            return None
        return f"{base_url.rstrip('/')}/files/{self.id}/thumbnail"

    @classmethod
    def get_file_type_from_mime(cls, mime_type: str) -> str:
        """MIMEタイプからファイル種別を判定."""
        if mime_type.startswith("image/"):
            return "image"
        elif mime_type == "application/pdf":
            return "pdf"
        elif mime_type.startswith("video/"):
            return "video"
        elif mime_type.startswith("audio/"):
            return "audio"
        elif mime_type in [
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "text/plain",
            "text/markdown",
            "text/csv",
        ]:
            return "document"
        else:
            return "other"

    @classmethod
    def get_extension_from_filename(cls, filename: str) -> str:
        """ファイル名から拡張子を取得."""
        from pathlib import Path

        return Path(filename).suffix.lower().lstrip(".")
