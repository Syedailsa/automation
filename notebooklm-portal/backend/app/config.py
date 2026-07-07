from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    PROJECT_NAME: str = "NotebookLM Portal"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/notebooklm_portal"
    DATABASE_ECHO: bool = False

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:80/auth/callback"

    # LLM Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    FIREWORKS_API_KEY: str = ""

    # LLM Settings
    LLM_DEFAULT_PROVIDER: str = "openrouter"
    LLM_DEFAULT_MODEL: str = "meta-llama/llama-3.3-70b-instruct:free"
    LLM_FALLBACK_PROVIDERS: str = "openrouter"
    LLM_MAX_RETRIES: int = 3
    LLM_TIMEOUT_SECONDS: int = 60

    # Storage
    NOTEBOOKLM_STORAGE_BASE: str = "storage/"

    # Upload limits
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: str = "pdf,txt,md,docx,csv,json"

    # CORS
    CORS_ORIGINS: str = "http://localhost:80"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Database Pool
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # Rate Limit Tiers (requests per hour, 0 = unlimited)
    RATE_LIMIT_FREE: int = 50
    RATE_LIMIT_PRO: int = 200
    RATE_LIMIT_ADMIN: int = 0


settings = Settings()
