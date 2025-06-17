"""Authentication API endpoints."""

from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_api_key,
    verify_email_verification_token,
    verify_password_reset_token,
    verify_refresh_token,
)
from app.crud import user as crud_user
from app.deps import get_current_active_user, get_current_user, get_db
from app.models.user import User
from app.schemas.user import (
    ApiKeyResponse,
    EmailConfirmation,
    EmailVerificationRequest,
    PasswordResetConfirmation,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserChangePassword,
    UserCreate,
    UserLogin,
    UserResetPassword,
)
from app.schemas.user import (
    User as UserSchema,
)

router = APIRouter()
security = HTTPBearer()


@router.post(
    "/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
def register(
    *,
    db: Annotated[Session, Depends(get_db)],
    user_in: UserCreate,
) -> Any:
    """新規ユーザー登録."""
    # メールアドレスの重複チェック
    if crud_user.user.get_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に登録されています",
        )

    # ユーザー名の重複チェック（指定されている場合）
    if user_in.username and crud_user.user.get_by_username(
        db, username=user_in.username
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このユーザー名は既に使用されています",
        )

    # ユーザー作成
    user = crud_user.user.create(db, obj_in=user_in)

    # TODO: メール認証トークンを生成してメール送信
    # verification_token = generate_email_verification_token(user.email)
    # send_verification_email(user.email, verification_token)

    return user


@router.post("/login", response_model=TokenResponse)
def login(
    *,
    db: Annotated[Session, Depends(get_db)],
    user_credentials: UserLogin,
) -> Any:
    """ユーザーログイン."""
    user = crud_user.user.authenticate(
        db,
        email_or_username=user_credentials.email_or_username,
        password=user_credentials.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレス/ユーザー名またはパスワードが正しくありません",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="アカウントが無効化されています",
        )

    # ログイン情報を更新
    crud_user.user.update_last_login(db, user=user)

    # トークンを生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        subject=user.email, expires_delta=refresh_token_expires
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    *,
    db: Annotated[Session, Depends(get_db)],
    refresh_request: RefreshTokenRequest,
) -> Any:
    """リフレッシュトークンを使用してアクセストークンを更新."""
    email = verify_refresh_token(refresh_request.refresh_token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なリフレッシュトークンです",
        )

    user = crud_user.user.get_by_email(db, email=email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザーが見つからないか、無効化されています",
        )

    # 新しいトークンを生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    new_refresh_token = create_refresh_token(
        subject=user.email, expires_delta=refresh_token_expires
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/change-password", response_model=dict[str, str])
def change_password(
    *,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    password_data: UserChangePassword,
) -> Any:
    """パスワード変更."""
    # 現在のパスワードを確認
    user = crud_user.user.authenticate(
        db,
        email_or_username=current_user.email,
        password=password_data.current_password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="現在のパスワードが正しくありません",
        )

    # 新しいパスワードを設定
    crud_user.user.update(
        db, db_obj=current_user, obj_in={"password": password_data.new_password}
    )

    return {"message": "パスワードが正常に変更されました"}


@router.post("/forgot-password", response_model=PasswordResetConfirmation)
def forgot_password(
    *,
    db: Annotated[Session, Depends(get_db)],
    reset_request: PasswordResetRequest,
) -> Any:
    """パスワードリセット要求."""
    user = crud_user.user.get_by_email(db, email=reset_request.email)
    if not user:
        # セキュリティのため、ユーザーが存在しない場合も成功レスポンスを返す
        return PasswordResetConfirmation(
            message="パスワードリセットの手順をメールで送信しました"
        )

    if not user.is_active:
        return PasswordResetConfirmation(
            message="パスワードリセットの手順をメールで送信しました"
        )

    # パスワードリセットトークンを生成
    # reset_token = generate_password_reset_token(user.email)

    # TODO: メール送信機能を実装
    # send_password_reset_email(user.email, reset_token)

    return PasswordResetConfirmation(
        message="パスワードリセットの手順をメールで送信しました"
    )


@router.post("/reset-password", response_model=dict[str, str])
def reset_password(
    *,
    db: Annotated[Session, Depends(get_db)],
    reset_data: UserResetPassword,
) -> Any:
    """パスワードリセット実行."""
    email = verify_password_reset_token(reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効または期限切れのトークンです",
        )

    user = crud_user.user.get_by_email(db, email=email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ユーザーが見つからないか、無効化されています",
        )

    # パスワードを更新
    crud_user.user.update(db, db_obj=user, obj_in={"password": reset_data.new_password})

    return {"message": "パスワードが正常にリセットされました"}


@router.post("/verify-email", response_model=EmailConfirmation)
def request_email_verification(
    *,
    db: Annotated[Session, Depends(get_db)],
    verification_request: EmailVerificationRequest,
) -> Any:
    """メール認証要求."""
    user = crud_user.user.get_by_email(db, email=verification_request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )

    if user.is_verified:
        return EmailConfirmation(message="このメールアドレスは既に認証済みです")

    # メール認証トークンを生成
    # verification_token = generate_email_verification_token(user.email)

    # TODO: メール送信機能を実装
    # send_verification_email(user.email, verification_token)

    return EmailConfirmation(message="認証メールを送信しました")


@router.post("/verify-email/{token}", response_model=dict[str, str])
def verify_email(
    *,
    db: Annotated[Session, Depends(get_db)],
    token: str,
) -> Any:
    """メール認証実行."""
    email = verify_email_verification_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効または期限切れのトークンです",
        )

    user = crud_user.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )

    if user.is_verified:
        return {"message": "このメールアドレスは既に認証済みです"}

    # メールアドレスを認証済みにする
    crud_user.user.verify_email(db, user=user)

    return {"message": "メールアドレスが正常に認証されました"}


@router.post("/api-key", response_model=ApiKeyResponse)
def generate_user_api_key(
    *,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """APIキーを生成."""
    # 新しいAPIキーを生成
    api_key = generate_api_key()

    # ユーザーにAPIキーを設定
    crud_user.user.update_api_key(db, user=current_user, api_key=api_key)

    return ApiKeyResponse(
        api_key=api_key,
        created_at=current_user.updated_at,
    )


@router.delete("/api-key", response_model=dict[str, str])
def revoke_api_key(
    *,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """APIキーを削除."""
    crud_user.user.remove_api_key(db, user=current_user)
    return {"message": "APIキーが正常に削除されました"}


@router.get("/me", response_model=UserSchema)
def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """現在のユーザー情報を取得."""
    return current_user


@router.post("/logout", response_model=dict[str, str])
def logout() -> Any:
    """ログアウト.

    Note: JWTはステートレスなので、実際にはクライアント側でトークンを削除する必要がある.
    将来的にはトークンブラックリスト機能を実装可能.
    """
    return {"message": "正常にログアウトしました"}
