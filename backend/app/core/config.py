"""
Central configuration for the whole backend.

Why this file exists:
Instead of scattering `os.getenv(...)` calls across the codebase, we load
every environment variable ONCE here into a typed `Settings` object. Every
other module imports `settings` from here. This makes it obvious what
configuration the app needs, and makes testing/overriding easy.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://aivoa_user:aivoa_pass@localhost:5432/aivoa_complaints"

    # Groq / LLM
    GROQ_API_KEY: str = ""
    GROQ_PRIMARY_MODEL: str = "gemma2-9b-it"
    GROQ_FALLBACK_MODEL: str = "llama-3.3-70b-versatile"

    # App
    APP_ENV: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    UPLOAD_DIR: str = "./uploads"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
