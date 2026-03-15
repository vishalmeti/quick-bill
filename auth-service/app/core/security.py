from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# bcrypt only accepts up to 72 bytes
BCRYPT_MAX_PASSWORD_BYTES = 72

ALGORITHM = "HS256"

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = timedelta(minutes=15)
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def _truncate_for_bcrypt(password: str) -> str:
    """Bcrypt accepts max 72 bytes; truncate to avoid ValueError."""
    pwd_bytes = password.encode("utf-8")
    if len(pwd_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        return pwd_bytes[:BCRYPT_MAX_PASSWORD_BYTES].decode("utf-8", errors="ignore")
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_truncate_for_bcrypt(plain_password), hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(_truncate_for_bcrypt(password))
