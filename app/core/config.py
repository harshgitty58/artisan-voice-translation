from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Artisan AI Business Copilot — Speech Translation"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Supabase PostgreSQL credentials
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None

    # Google Cloud API configuration
    GOOGLE_CLOUD_API_KEY: Optional[str] = None

    # Hugging Face Fine-Tuned Model Configuration
    HF_MODEL_REPO: str = "harshvdn2/qwen-artisan-description"
    HF_TOKEN: Optional[str] = None

    # Render deployment configuration
    RENDER_EXTERNAL_URL: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
