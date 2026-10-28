# TransitMatrix - Security and Cryptography Module
# Provides bcrypt password hashing and JWT token creation/decoding.

from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import settings

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a stored bcrypt hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: Any, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a signed JWT access token containing subject (user_id/username) and role claims.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decodes and validates a JWT token using the configured secret key.
    Raises JWTError if signature is invalid or token has expired.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
