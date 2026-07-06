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

    # Storage
    NOTEBOOKLM_STORAGE_BASE: str = "storage/"

    # CORS
    CORS_ORIGINS: str = "http://localhost:80"


settings = Settings()
