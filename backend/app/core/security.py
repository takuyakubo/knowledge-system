"""Security utilities for authentication and authorization."""

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# パスワードハッシュ化コンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT設定
ALGORITHM = "HS256"


def create_access_token(
    subject: str | Any, expires_delta: timedelta | None = None
) -> str:
    """JWTアクセストークンを作成."""
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: str | Any, expires_delta: timedelta | None = None
) -> str:
    """JWTリフレッシュトークンを作成."""
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> str | None:
    """JWTトークンを検証してsubjectを返す."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = payload.get("sub")
        return token_data
    except JWTError:
        return None


def verify_refresh_token(token: str) -> str | None:
    """リフレッシュトークンを検証してsubjectを返す."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        if token_type != "refresh":
            return None
        token_data = payload.get("sub")
        return token_data
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """プレーンパスワードとハッシュ化パスワードを照合."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """パスワードをハッシュ化."""
    return pwd_context.hash(password)


def generate_password_reset_token(email: str) -> str:
    """パスワードリセット用トークンを生成."""
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(UTC)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email}, settings.SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    """パスワードリセットトークンを検証."""
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token["sub"]
    except JWTError:
        return None


def generate_email_verification_token(email: str) -> str:
    """メール認証用トークンを生成."""
    delta = timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    now = datetime.now(UTC)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": "email_verification"},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def verify_email_verification_token(token: str) -> str | None:
    """メール認証トークンを検証."""
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if decoded_token.get("type") != "email_verification":
            return None
        return decoded_token["sub"]
    except JWTError:
        return None


def generate_api_key() -> str:
    """APIキーを生成."""
    return secrets.token_urlsafe(32)


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """パスワード強度を検証."""
    errors = []

    if len(password) < 8:
        errors.append("パスワードは8文字以上である必要があります")

    if len(password) > 128:
        errors.append("パスワードは128文字以下である必要があります")

    if not any(c.islower() for c in password):
        errors.append("パスワードには小文字を含める必要があります")

    if not any(c.isupper() for c in password):
        errors.append("パスワードには大文字を含める必要があります")

    if not any(c.isdigit() for c in password):
        errors.append("パスワードには数字を含める必要があります")

    # 特殊文字チェック
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("パスワードには特殊文字を含める必要があります")

    return len(errors) == 0, errors


def check_common_passwords(password: str) -> bool:
    """よく使われるパスワードかどうかをチェック."""
    # 簡単なよく使われるパスワードのリスト
    common_passwords = {
        "password",
        "123456",
        "123456789",
        "qwerty",
        "abc123",
        "password123",
        "admin",
        "letmein",
        "welcome",
        "monkey",
        "1234567890",
        "password1",
        "123123",
        "qwertyuiop",
    }

    return password.lower() in common_passwords


def generate_secure_random_string(length: int = 32) -> str:
    """セキュアなランダム文字列を生成."""
    return secrets.token_urlsafe(length)


def hash_api_key(api_key: str) -> str:
    """APIキーをハッシュ化（データベース保存用）."""
    return get_password_hash(api_key)


def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """APIキーを検証."""
    return verify_password(plain_api_key, hashed_api_key)


class SecurityHeaders:
    """セキュリティヘッダーの定義."""

    @staticmethod
    def get_headers() -> dict[str, str]:
        """セキュリティヘッダーを取得."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
        }


def create_csrf_token() -> str:
    """CSRF保護用トークンを生成."""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, expected_token: str) -> bool:
    """CSRFトークンを検証."""
    return secrets.compare_digest(token, expected_token)
