# TransitMatrix - API Dependencies Module
# Handles JWT authentication verification and Role-Based Access Control (RBAC).

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from typing import Dict, Any, List
from app.core.security import decode_access_token
from app.db.connection import get_db_connection
from app.repositories.user_repository import UserRepository

# OAuth2 scheme extracting Bearer token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Decodes the Bearer token, fetches the user from MySQL, and validates active status.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    with get_db_connection() as conn:
        user = UserRepository.get_by_id(conn, user_id)
        if user is None:
            raise credentials_exception
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive."
            )
        return user


def require_roles(*allowed_roles: str):
    """
    Dependency factory that checks if the authenticated user has one of the allowed roles.
    Example: Depends(require_roles("ADMIN", "STAFF"))
    """
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Requires role in: {list(allowed_roles)}"
            )
        return current_user

    return role_checker
