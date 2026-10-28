# TransitMatrix - Authentication Routes
# Endpoints for user registration, login, and profile access.

from fastapi import APIRouter, Depends, status
from typing import Dict, Any
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserProfileResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
def register(request: UserRegisterRequest):
    """
    Register a new user account with validated credentials.
    """
    return AuthService.register_user(request)


@router.post("/login", response_model=TokenResponse)
def login(request: UserLoginRequest):
    """
    Authenticate user and generate JWT access token.
    """
    return AuthService.authenticate_user(request)


@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Fetch profile information of the currently authenticated user.
    """
    return AuthService.get_user_profile(current_user["user_id"])
