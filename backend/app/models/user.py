"""User model for authentication and user management."""

from datetime import datetime

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """ユーザーを管理するモデル."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, doc="ユーザーID")

    # 基本情報
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True, doc="メールアドレス"
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, doc="ユーザー名"
    )
    full_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True, doc="フルネーム"
    )

    # 認証情報
    hashed_password: Mapped[str] = mapped_column(
        String(128), nullable=False, doc="ハッシュ化されたパスワード"
    )

    # アカウント状態
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, doc="アカウント有効フラグ"
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, doc="メール認証済みフラグ"
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, doc="スーパーユーザーフラグ"
    )

    # プロフィール情報
    bio: Mapped[str | None] = mapped_column(Text, nullable=True, doc="自己紹介")
    avatar_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, doc="アバター画像URL"
    )
    website_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, doc="ウェブサイトURL"
    )
    github_username: Mapped[str | None] = mapped_column(
        String(100), nullable=True, doc="GitHubユーザー名"
    )
    twitter_username: Mapped[str | None] = mapped_column(
        String(100), nullable=True, doc="Twitterユーザー名"
    )

    # タイムゾーン・設定
    timezone: Mapped[str] = mapped_column(
        String(50), default="UTC", nullable=False, doc="タイムゾーン"
    )
    language: Mapped[str] = mapped_column(
        String(10), default="ja", nullable=False, doc="言語設定"
    )

    # ログイン記録
    last_login_at: Mapped[datetime | None] = mapped_column(
        nullable=True, doc="最終ログイン日時"
    )
    login_count: Mapped[int] = mapped_column(
        default=0, nullable=False, doc="ログイン回数"
    )

    # API アクセス
    api_key: Mapped[str | None] = mapped_column(
        String(64), unique=True, nullable=True, doc="APIキー"
    )

    # リレーション (将来的に追加)
    # articles: Mapped[list["Article"]] = relationship(
    #     "Article", back_populates="author"
    # )
    # papers: Mapped[list["Paper"]] = relationship(
    #     "Paper", back_populates="added_by"
    # )

    def __repr__(self) -> str:
        """デバッグ用の文字列表現."""
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"

    @property
    def display_name(self) -> str:
        """表示用の名前を取得."""
        return self.full_name or self.username

    def is_email_verified(self) -> bool:
        """メールアドレスが認証済みかどうか."""
        return self.is_verified

    def can_access_admin(self) -> bool:
        """管理者機能にアクセス可能かどうか."""
        return self.is_superuser and self.is_active

    def update_login_info(self) -> None:
        """ログイン情報を更新."""
        self.last_login_at = datetime.now()
        self.login_count += 1

    def deactivate(self) -> None:
        """アカウントを無効化."""
        self.is_active = False

    def activate(self) -> None:
        """アカウントを有効化."""
        self.is_active = True

    def verify_email(self) -> None:
        """メールアドレスを認証済みにする."""
        self.is_verified = True

    def make_superuser(self) -> None:
        """スーパーユーザーにする."""
        self.is_superuser = True

    def revoke_superuser(self) -> None:
        """スーパーユーザー権限を取り消す."""
        self.is_superuser = False

    @classmethod
    def create_username_from_email(cls, email: str) -> str:
        """メールアドレスからユーザー名を生成."""
        import re

        # メールアドレスのローカル部分を取得
        local_part = email.split("@")[0]

        # 英数字とアンダースコアのみに変換
        username = re.sub(r"[^\w]", "_", local_part)

        # 先頭と末尾のアンダースコアを削除
        username = username.strip("_")

        # 空の場合はデフォルト値
        return username or "user"
