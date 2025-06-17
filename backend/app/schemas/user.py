"""User schemas for API endpoints."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.security import check_common_passwords, validate_password_strength


class UserBase(BaseModel):
    """User base schema."""

    email: EmailStr = Field(..., description="メールアドレス")
    username: str | None = Field(
        None, min_length=3, max_length=50, description="ユーザー名"
    )
    full_name: str | None = Field(None, max_length=100, description="フルネーム")
    bio: str | None = Field(None, max_length=1000, description="自己紹介")
    avatar_url: str | None = Field(None, description="アバター画像URL")
    website_url: str | None = Field(None, description="ウェブサイトURL")
    github_username: str | None = Field(
        None, max_length=100, description="GitHubユーザー名"
    )
    twitter_username: str | None = Field(
        None, max_length=100, description="Twitterユーザー名"
    )
    timezone: str = Field(default="UTC", description="タイムゾーン")
    language: str = Field(default="ja", description="言語設定")


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8, max_length=128, description="パスワード")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """パスワードの強度を検証."""
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError(f"パスワードが弱すぎます: {', '.join(errors)}")

        if check_common_passwords(v):
            raise ValueError("よく使われるパスワードは使用できません")

        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        """ユーザー名の検証."""
        if v is None:
            return v

        # 英数字とアンダースコアのみ許可
        import re

        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("ユーザー名は英数字とアンダースコアのみ使用できます")

        return v


class UserUpdate(BaseModel):
    """User update schema."""

    email: EmailStr | None = Field(None, description="メールアドレス")
    username: str | None = Field(
        None, min_length=3, max_length=50, description="ユーザー名"
    )
    full_name: str | None = Field(None, max_length=100, description="フルネーム")
    bio: str | None = Field(None, max_length=1000, description="自己紹介")
    avatar_url: str | None = Field(None, description="アバター画像URL")
    website_url: str | None = Field(None, description="ウェブサイトURL")
    github_username: str | None = Field(
        None, max_length=100, description="GitHubユーザー名"
    )
    twitter_username: str | None = Field(
        None, max_length=100, description="Twitterユーザー名"
    )
    timezone: str | None = Field(None, description="タイムゾーン")
    language: str | None = Field(None, description="言語設定")
    password: str | None = Field(
        None, min_length=8, max_length=128, description="新しいパスワード"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        """パスワードの強度を検証."""
        if v is None:
            return v

        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError(f"パスワードが弱すぎます: {', '.join(errors)}")

        if check_common_passwords(v):
            raise ValueError("よく使われるパスワードは使用できません")

        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        """ユーザー名の検証."""
        if v is None:
            return v

        # 英数字とアンダースコアのみ許可
        import re

        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("ユーザー名は英数字とアンダースコアのみ使用できます")

        return v


class UserAdminUpdate(UserUpdate):
    """Admin user update schema."""

    is_active: bool | None = Field(None, description="アカウント有効フラグ")
    is_verified: bool | None = Field(None, description="メール認証済みフラグ")
    is_superuser: bool | None = Field(None, description="スーパーユーザーフラグ")


class UserLogin(BaseModel):
    """User login schema."""

    email_or_username: str = Field(..., description="メールアドレスまたはユーザー名")
    password: str = Field(..., description="パスワード")


class UserChangePassword(BaseModel):
    """Password change schema."""

    current_password: str = Field(..., description="現在のパスワード")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="新しいパスワード"
    )

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """パスワードの強度を検証."""
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError(f"パスワードが弱すぎます: {', '.join(errors)}")

        if check_common_passwords(v):
            raise ValueError("よく使われるパスワードは使用できません")

        return v


class UserResetPassword(BaseModel):
    """Password reset schema."""

    token: str = Field(..., description="パスワードリセットトークン")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="新しいパスワード"
    )

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """パスワードの強度を検証."""
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError(f"パスワードが弱すぎます: {', '.join(errors)}")

        if check_common_passwords(v):
            raise ValueError("よく使われるパスワードは使用できません")

        return v


class UserProfile(BaseModel):
    """User profile response schema."""

    id: int = Field(..., description="ユーザーID")
    email: EmailStr = Field(..., description="メールアドレス")
    username: str = Field(..., description="ユーザー名")
    full_name: str | None = Field(None, description="フルネーム")
    display_name: str = Field(..., description="表示名")
    bio: str | None = Field(None, description="自己紹介")
    avatar_url: str | None = Field(None, description="アバター画像URL")
    website_url: str | None = Field(None, description="ウェブサイトURL")
    github_username: str | None = Field(None, description="GitHubユーザー名")
    twitter_username: str | None = Field(None, description="Twitterユーザー名")
    timezone: str = Field(..., description="タイムゾーン")
    language: str = Field(..., description="言語設定")
    is_verified: bool = Field(..., description="メール認証済みフラグ")
    created_at: datetime = Field(..., description="作成日時")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class User(UserProfile):
    """Full user response schema."""

    is_active: bool = Field(..., description="アカウント有効フラグ")
    is_superuser: bool = Field(..., description="スーパーユーザーフラグ")
    last_login_at: datetime | None = Field(None, description="最終ログイン日時")
    login_count: int = Field(..., description="ログイン回数")
    updated_at: datetime = Field(..., description="更新日時")


class UserStats(BaseModel):
    """User statistics schema."""

    total_users: int = Field(..., description="総ユーザー数")
    active_users: int = Field(..., description="アクティブユーザー数")
    verified_users: int = Field(..., description="認証済みユーザー数")
    superusers: int = Field(..., description="スーパーユーザー数")
    recent_registrations: list[User] = Field(..., description="最近の登録ユーザー")


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str = Field(..., description="アクセストークン")
    refresh_token: str = Field(..., description="リフレッシュトークン")
    token_type: str = Field(default="bearer", description="トークンタイプ")
    expires_in: int = Field(..., description="トークン有効期限(秒)")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str = Field(..., description="リフレッシュトークン")


class EmailVerificationRequest(BaseModel):
    """Email verification request schema."""

    email: EmailStr = Field(..., description="認証するメールアドレス")


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""

    email: EmailStr = Field(..., description="パスワードリセット対象のメールアドレス")


class ApiKeyResponse(BaseModel):
    """API key response schema."""

    api_key: str = Field(..., description="生成されたAPIキー")
    created_at: datetime = Field(..., description="作成日時")


class UserSearchResult(BaseModel):
    """User search result schema."""

    users: list[User] = Field(..., description="ユーザーリスト")
    total: int = Field(..., description="総件数")
    page: int = Field(..., description="ページ番号")
    size: int = Field(..., description="ページサイズ")
    has_next: bool = Field(..., description="次のページがあるか")


# パスワード忘れ・メール認証用のスキーマ
class EmailConfirmation(BaseModel):
    """Email confirmation schema."""

    message: str = Field(..., description="確認メッセージ")


class PasswordResetConfirmation(BaseModel):
    """Password reset confirmation schema."""

    message: str = Field(..., description="パスワードリセット確認メッセージ")
