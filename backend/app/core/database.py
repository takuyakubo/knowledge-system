"""Database configuration and session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models.base import Base  # 新しいBaseクラスをインポート

# SQLAlchemy エンジンの作成
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 接続の健全性チェック
    echo=settings.DEBUG,  # デバッグモードでSQL出力
)

# セッションファクトリの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """データベースセッションの依存性注入用ジェネレータ."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """テーブルの作成."""
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """テーブルの削除（テスト用）."""
    Base.metadata.drop_all(bind=engine)
