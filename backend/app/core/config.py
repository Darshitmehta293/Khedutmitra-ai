"""
KhedutMitra AI — Core Settings
"""
from functools import lru_cache
import os
from typing import List, Optional
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def ignore_empty_environment_values(cls, values: object) -> object:
        if isinstance(values, dict):
            cleaned = {key: value for key, value in values.items() if value != ""}
            return cleaned
        return values

    @model_validator(mode="after")
    def use_vercel_database_path(self) -> "Settings":
        if os.getenv("VERCEL"):
            if self.DATABASE_URL.startswith("sqlite"):
                raise ValueError("DATABASE_URL must point to a persistent PostgreSQL database on Vercel")
            if self.DATABASE_URL.startswith("postgres://"):
                self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
            elif self.DATABASE_URL.startswith("postgresql://"):
                self.DATABASE_URL = self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            if not self.SYNC_DATABASE_URL.strip() or self.SYNC_DATABASE_URL.startswith("sqlite"):
                self.SYNC_DATABASE_URL = self.DATABASE_URL.replace(
                    "postgresql+asyncpg://", "postgresql://", 1
                )
            elif self.SYNC_DATABASE_URL.startswith("postgres://"):
                self.SYNC_DATABASE_URL = self.SYNC_DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self

    # App
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    PROJECT_NAME: str = "KhedutMitra AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-Powered Cotton & Groundnut Market Linkage Platform"

    # Database (defaults to SQLite for zero-dependency local dev; override with PostgreSQL URL for production)
    DATABASE_URL: str = "sqlite+aiosqlite:///./khedutmitra.db"
    SYNC_DATABASE_URL: str = "sqlite:///./khedutmitra.db"

    # Security
    JWT_SECRET: str = "dev-secret-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    BCRYPT_ROUNDS: int = 12

    # IBM Watson
    IBM_API_KEY: Optional[str] = None
    IBM_PROJECT_ID: Optional[str] = None
    IBM_GRANITE_ENDPOINT: str = "https://us-south.ml.cloud.ibm.com"
    IBM_GRANITE_MODEL_ID: str = "ibm/granite-13b-instruct-v2"
    IBM_IAM_URL: str = "https://iam.cloud.ibm.com/identity/token"

    # IBM COS
    COS_API_KEY: Optional[str] = None
    COS_INSTANCE_ID: Optional[str] = None
    COS_ENDPOINT: str = "https://s3.us-south.cloud-object-storage.appdomain.cloud"
    COS_BUCKET: str = "khedutmitra-images"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Market Data
    MARKET_DATA_PROVIDER: str = "mock"
    LIVE_MARKET_DATA_API_URL: Optional[str] = None
    LIVE_MARKET_DATA_API_KEY: Optional[str] = None

    # Upload
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp"

    @field_validator("MAX_UPLOAD_SIZE_MB", mode="before")
    @classmethod
    def parse_upload_size(cls, value: object) -> object:
        if isinstance(value, str):
            digits = "".join(character for character in value if character.isdigit())
            return int(digits) if digits else 5
        return value

    # Feature Flags
    ENABLE_QUALITY_AI: bool = False
    ENABLE_LIVE_MARKET_DATA: bool = False
    DEMO_MODE: bool = True

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    @property
    def allowed_image_types_list(self) -> List[str]:
        return [t.strip() for t in self.ALLOWED_IMAGE_TYPES.split(",")]

    @property
    def is_granite_configured(self) -> bool:
        return bool(self.IBM_API_KEY and self.IBM_PROJECT_ID)

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
