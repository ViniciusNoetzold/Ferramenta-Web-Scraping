"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Global settings — loaded from .env file."""

    # --------------- API Keys ---------------
    NVIDIA_API_KEY: Optional[str] = None
    GROK_API_KEY: Optional[str] = None  # Groq-compatible key

    # --------------- Database ---------------
    DATABASE_URL: str = "sqlite+aiosqlite:///./webarchiver.db"

    # --------------- Scraping ---------------
    MAX_CONCURRENT_SCRAPES: int = 3
    RATE_LIMIT_DELAY: float = 1.0
    REQUEST_TIMEOUT: int = 30
    DOWNLOAD_IMAGES: bool = True

    # --------------- Output ---------------
    OUTPUT_DIR: str = "./output"

    # --------------- AI Models ---------------
    NVIDIA_MODEL: str = "nvidia/llama-3.1-nemotron-ultra-253b-v1"
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    GROK_MODEL: str = "llama-3.3-70b-versatile"
    GROK_BASE_URL: str = "https://api.groq.com/openai/v1"

    # --------------- Server ---------------
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # --------------- Celery ---------------
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def ai_available(self) -> bool:
        """Check if at least one AI provider is configured."""
        return bool(self.NVIDIA_API_KEY or self.GROK_API_KEY)


settings = Settings()
