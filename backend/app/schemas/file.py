"""File schemas for API endpoints."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class FileBase(BaseModel):
    """File base schema."""

    filename: str = Field(..., max_length=255, description="ファイル名")
    original_filename: str = Field(..., max_length=255, description="元のファイル名")
    description: str | None = Field(None, max_length=500, description="ファイルの説明")
    alt_text: str | None = Field(None, max_length=255, description="画像の代替テキスト")
    is_public: bool = Field(default=True, description="公開フラグ")
    article_id: int | None = Field(None, description="関連記事ID")
    paper_id: int | None = Field(None, description="関連論文ID")


class FileCreate(FileBase):
    """File creation schema."""

    file_path: str = Field(..., max_length=500, description="ファイルパス")
    file_size: int = Field(..., ge=0, description="ファイルサイズ(バイト)")
    mime_type: str = Field(..., max_length=100, description="MIMEタイプ")
    file_extension: str = Field(..., max_length=10, description="ファイル拡張子")
    file_hash: str | None = Field(None, max_length=64, description="ファイルハッシュ")
    file_type: str = Field(..., max_length=20, description="ファイル種別")
    width: int | None = Field(None, ge=0, description="画像幅(ピクセル)")
    height: int | None = Field(None, ge=0, description="画像高さ(ピクセル)")
    has_thumbnail: bool = Field(default=False, description="サムネイル有無")
    thumbnail_path: str | None = Field(
        None, max_length=500, description="サムネイルパス"
    )

    @field_validator("file_type")
    @classmethod
    def validate_file_type(cls, v: str) -> str:
        """ファイルタイプの検証."""
        allowed_types = ["image", "document", "pdf", "video", "audio", "other"]
        if v not in allowed_types:
            raise ValueError(
                f"ファイルタイプは {allowed_types} のいずれかである必要があります"
            )
        return v


class FileUpdate(BaseModel):
    """File update schema."""

    filename: str | None = Field(None, max_length=255, description="ファイル名")
    description: str | None = Field(None, max_length=500, description="ファイルの説明")
    alt_text: str | None = Field(None, max_length=255, description="画像の代替テキスト")
    is_public: bool | None = Field(None, description="公開フラグ")
    article_id: int | None = Field(None, description="関連記事ID")
    paper_id: int | None = Field(None, description="関連論文ID")


class FileUploadResponse(BaseModel):
    """File upload response schema."""

    file_id: int = Field(..., description="アップロードされたファイルID")
    filename: str = Field(..., description="ファイル名")
    file_size: int = Field(..., description="ファイルサイズ(バイト)")
    file_size_readable: str = Field(..., description="読みやすいファイルサイズ")
    mime_type: str = Field(..., description="MIMEタイプ")
    file_type: str = Field(..., description="ファイル種別")
    url: str = Field(..., description="ファイルアクセスURL")
    thumbnail_url: str | None = Field(None, description="サムネイルURL")
    is_image: bool = Field(..., description="画像ファイルか")
    width: int | None = Field(None, description="画像幅")
    height: int | None = Field(None, description="画像高さ")


class FileBulkUploadResponse(BaseModel):
    """Bulk file upload response schema."""

    uploaded_files: list[FileUploadResponse] = Field(
        ..., description="アップロード成功ファイル"
    )
    failed_files: list[dict[str, Any]] = Field(
        ..., description="アップロード失敗ファイル"
    )
    total_files: int = Field(..., description="総ファイル数")
    success_count: int = Field(..., description="成功数")
    failure_count: int = Field(..., description="失敗数")


class FileStats(BaseModel):
    """File statistics schema."""

    total_files: int = Field(..., description="総ファイル数")
    total_size: int = Field(..., description="総ファイルサイズ(バイト)")
    total_size_readable: str = Field(..., description="読みやすい総サイズ")
    by_type: dict[str, int] = Field(..., description="ファイルタイプ別数")
    by_extension: dict[str, int] = Field(..., description="拡張子別数")
    average_size: float = Field(..., description="平均ファイルサイズ(MB)")
    largest_file: dict[str, Any] | None = Field(None, description="最大ファイル情報")


class FileSearchResult(BaseModel):
    """File search result schema."""

    files: list["File"] = Field(..., description="ファイルリスト")
    total: int = Field(..., description="総件数")
    page: int = Field(..., description="ページ番号")
    size: int = Field(..., description="ページサイズ")
    has_next: bool = Field(..., description="次のページがあるか")


class File(FileBase):
    """File response schema."""

    id: int = Field(..., description="ファイルID")
    file_path: str = Field(..., description="ファイルパス")
    file_size: int = Field(..., description="ファイルサイズ(バイト)")
    file_size_mb: float = Field(..., description="ファイルサイズ(MB)")
    file_size_readable: str = Field(..., description="読みやすいファイルサイズ")
    mime_type: str = Field(..., description="MIMEタイプ")
    file_extension: str = Field(..., description="ファイル拡張子")
    file_hash: str | None = Field(None, description="ファイルハッシュ")
    file_type: str = Field(..., description="ファイル種別")
    width: int | None = Field(None, description="画像幅(ピクセル)")
    height: int | None = Field(None, description="画像高さ(ピクセル)")
    download_count: int = Field(..., description="ダウンロード数")
    has_thumbnail: bool = Field(..., description="サムネイル有無")
    thumbnail_path: str | None = Field(None, description="サムネイルパス")
    is_image: bool = Field(..., description="画像ファイルか")
    is_pdf: bool = Field(..., description="PDFファイルか")
    is_document: bool = Field(..., description="ドキュメントファイルか")
    url: str = Field(..., description="ファイルアクセスURL")
    thumbnail_url: str | None = Field(None, description="サムネイルURL")
    created_at: str = Field(..., description="作成日時")
    updated_at: str = Field(..., description="更新日時")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# 循環参照の解決
FileSearchResult.model_rebuild()
