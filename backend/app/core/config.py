# TransitMatrix - Configuration Module
# Loads application and MySQL database configuration from environment variables

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "TransitMatrix"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # MySQL database connection settings
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "transitmatrix"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_POOL_SIZE: int = 10
    MYSQL_POOL_NAME: str = "transitmatrix_pool"

    # JWT Authentication and Security
    SECRET_KEY: str = "change_this_to_a_super_secret_jwt_key_at_least_32_chars_long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # Server environment
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]

    # Machine Learning Settings
    ML_MODEL_VERSION: str = "v1.0"
    ML_MODELS_DIR: str = "./ml/models"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
