# TransitMatrix - Authentication Service
# Handles business logic for user registration, login, and profile retrieval.

from fastapi import HTTPException, status
from app.db.connection import get_db_connection
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserProfileResponse


class AuthService:

    @staticmethod
    def register_user(request: UserRegisterRequest) -> UserProfileResponse:
        """
        Validates uniqueness of username and email, hashes the password,
        and creates a new user record in the database.
        """
        with get_db_connection() as conn:
            # Check if username is already taken
            existing_user = UserRepository.get_by_username(conn, request.username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Username '{request.username}' is already registered."
                )

            # Check if email is already taken
            existing_email = UserRepository.get_by_email(conn, request.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email '{request.email}' is already registered."
                )

            # Hash the plain password
            hashed_pwd = hash_password(request.password)

            # Insert new user record
            user_id = UserRepository.create_user(
                connection=conn,
                username=request.username,
                email=request.email,
                password_hash=hashed_pwd,
                role=request.role,
                first_name=request.first_name,
                last_name=request.last_name,
                phone_number=request.phone_number
            )
            conn.commit()

            # Retrieve newly created user
            new_user = UserRepository.get_by_id(conn, user_id)
            return UserProfileResponse(**new_user)

    @staticmethod
    def authenticate_user(request: UserLoginRequest) -> TokenResponse:
        """
        Authenticates a user by username and password, then issues a JWT access token.
        """
        with get_db_connection() as conn:
            user = UserRepository.get_by_username(conn, request.username)
            if not user or not verify_password(request.password, user["password_hash"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if not user.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is deactivated."
                )

            # Create JWT token with user_id and role
            token = create_access_token(subject=user["user_id"], role=user["role"])

            return TokenResponse(
                access_token=token,
                token_type="bearer",
                user_id=user["user_id"],
                username=user["username"],
                role=user["role"]
            )

    @staticmethod
    def get_user_profile(user_id: int) -> UserProfileResponse:
        """
        Retrieves user profile details by user ID.
        """
        with get_db_connection() as conn:
            user = UserRepository.get_by_id(conn, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found."
                )
            return UserProfileResponse(**user)
