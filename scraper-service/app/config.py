"""Application settings and configuration management.

Uses pydantic-settings to load configuration from environment variables
and .env files with validation and type coercion.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Server Configuration ---
    host: str = "0.0.0.0"
    port: int = 3011
    debug: bool = False

    # --- CORS ---
    cors_origins: str = "*"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse CORS_ORIGINS into a list of allowed origins."""
        if self.cors_origins == "*":
            return ["*"]
            
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton)."""
    return Settings()
