"""Production configuration overrides."""
from app.config import Settings


class ProductionSettings(Settings):
    DEBUG: bool = False
    DATABASE_ECHO: bool = False
    CORS_ORIGINS: str = "https://yourdomain.com"


production_settings = ProductionSettings()
