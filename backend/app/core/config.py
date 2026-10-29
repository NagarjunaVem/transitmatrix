# TransitMatrix - Configuration Module
# Loads application and MySQL database configuration from environment variables or .env file

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

# Discover .env from current directory, backend directory, or project root
_curr_dir = os.path.abspath(os.getcwd())
_file_dir = os.path.dirname(os.path.abspath(__file__))
_app_dir = os.path.dirname(_file_dir)
_backend_dir = os.path.dirname(_app_dir)
_root_dir = os.path.dirname(_backend_dir)

_env_candidates = [
    os.path.join(_curr_dir, ".env"),
    os.path.join(_root_dir, ".env"),
    os.path.join(_backend_dir, ".env"),
]
_env_file = next((f for f in _env_candidates if os.path.isfile(f)), ".env")


class Settings(BaseSettings):
    PROJECT_NAME: str = "TransitMatrix"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # MySQL database connection settings
    # Default to empty password for standard XAMPP/local dev; overridable via .env
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "transitmatrix"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_POOL_SIZE: int = 10
    MYSQL_POOL_NAME: str = "transitmatrix_pool"

    # JWT Authentication and Security
    SECRET_KEY: str = "transitmatrix_super_secret_jwt_key_at_least_32_chars_long_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # Server environment
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Machine Learning Settings
    ML_MODEL_VERSION: str = "v1.0"
    ML_MODELS_DIR: str = "./ml/models"

    model_config = SettingsConfigDict(
        env_file=_env_file,
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
