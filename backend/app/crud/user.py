"""User CRUD operations."""

from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """User CRUD operations."""

    def get_by_email(self, db: Session, *, email: str) -> User | None:
        """メールアドレスでユーザーを取得."""
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> User | None:
        """ユーザー名でユーザーを取得."""
        return db.query(User).filter(User.username == username).first()

    def get_by_api_key(self, db: Session, *, api_key: str) -> User | None:
        """APIキーでユーザーを取得."""
        return db.query(User).filter(User.api_key == api_key).first()

    def get_by_email_or_username(
        self, db: Session, *, email_or_username: str
    ) -> User | None:
        """メールアドレスまたはユーザー名でユーザーを取得."""
        return (
            db.query(User)
            .filter(
                or_(
                    User.email == email_or_username,
                    User.username == email_or_username,
                )
            )
            .first()
        )

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """新しいユーザーを作成."""
        # パスワードをハッシュ化
        hashed_password = get_password_hash(obj_in.password)

        # ユーザー名が提供されていない場合、メールから生成
        username = obj_in.username
        if not username:
            username = User.create_username_from_email(obj_in.email)
            # ユーザー名の重複をチェックして調整
            base_username = username
            counter = 1
            while self.get_by_username(db, username=username):
                username = f"{base_username}_{counter}"
                counter += 1

        create_data = obj_in.model_dump(exclude={"password"})
        create_data.update(
            {
                "hashed_password": hashed_password,
                "username": username,
            }
        )

        db_obj = User(**create_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: UserUpdate | dict[str, Any]
    ) -> User:
        """ユーザー情報を更新."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # パスワードが含まれている場合はハッシュ化
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(
        self, db: Session, *, email_or_username: str, password: str
    ) -> User | None:
        """ユーザー認証."""
        user = self.get_by_email_or_username(db, email_or_username=email_or_username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """ユーザーがアクティブかどうか."""
        return user.is_active

    def is_verified(self, user: User) -> bool:
        """ユーザーのメールが認証済みかどうか."""
        return user.is_verified

    def is_superuser(self, user: User) -> bool:
        """ユーザーがスーパーユーザーかどうか."""
        return user.is_superuser

    def verify_email(self, db: Session, *, user: User) -> User:
        """メールアドレスを認証済みにする."""
        user.verify_email()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def activate(self, db: Session, *, user: User) -> User:
        """ユーザーを有効化."""
        user.activate()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def deactivate(self, db: Session, *, user: User) -> User:
        """ユーザーを無効化."""
        user.deactivate()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def make_superuser(self, db: Session, *, user: User) -> User:
        """ユーザーをスーパーユーザーにする."""
        user.make_superuser()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def revoke_superuser(self, db: Session, *, user: User) -> User:
        """スーパーユーザー権限を取り消す."""
        user.revoke_superuser()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_last_login(self, db: Session, *, user: User) -> User:
        """最終ログイン情報を更新."""
        user.update_login_info()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def search_users(
        self,
        db: Session,
        *,
        query: str,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> list[User]:
        """ユーザーを検索."""
        q = db.query(User)

        if not include_inactive:
            q = q.filter(User.is_active.is_(True))

        if query:
            # メール、ユーザー名、フルネームで検索
            search_filter = or_(
                User.email.ilike(f"%{query}%"),
                User.username.ilike(f"%{query}%"),
                User.full_name.ilike(f"%{query}%"),
            )
            q = q.filter(search_filter)

        return q.offset(skip).limit(limit).all()

    def get_users_by_role(
        self,
        db: Session,
        *,
        is_superuser: bool | None = None,
        is_verified: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """ロール・ステータス別でユーザーを取得."""
        q = db.query(User).filter(User.is_active.is_(True))

        if is_superuser is not None:
            q = q.filter(User.is_superuser.is_(is_superuser))

        if is_verified is not None:
            q = q.filter(User.is_verified.is_(is_verified))

        return q.offset(skip).limit(limit).all()

    def get_active_count(self, db: Session) -> int:
        """アクティブユーザー数を取得."""
        return db.query(User).filter(User.is_active.is_(True)).count()

    def get_recent_users(self, db: Session, *, limit: int = 10) -> list[User]:
        """最近登録されたユーザーを取得."""
        return (
            db.query(User)
            .filter(User.is_active.is_(True))
            .order_by(User.created_at.desc())
            .limit(limit)
            .all()
        )

    def check_email_exists(self, db: Session, *, email: str) -> bool:
        """メールアドレスが既に存在するかチェック."""
        return db.query(User).filter(User.email == email).first() is not None

    def check_username_exists(self, db: Session, *, username: str) -> bool:
        """ユーザー名が既に存在するかチェック."""
        return db.query(User).filter(User.username == username).first() is not None

    def update_api_key(self, db: Session, *, user: User, api_key: str) -> User:
        """APIキーを更新."""
        user.api_key = api_key
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def remove_api_key(self, db: Session, *, user: User) -> User:
        """APIキーを削除."""
        user.api_key = None
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user = CRUDUser(User)
