from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]

DEFAULT_GEMINI_MODEL = "gemini-3.8-flash"

# Railway/UI may still have retired aliases set in GEMINI_MODEL.
RETIRED_GEMINI_MODELS = {
    "gemini-flash-latest",
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    # Preview alias fails when the client hits API v1 instead of v1beta.
    "gemini-3-flash-preview",
}


class Settings(BaseSettings):
    gemini_api_key: str = ""
    assemblyai_api_key: str = ""
    gemini_model: str = DEFAULT_GEMINI_MODEL
    cors_origins: str = "http://localhost:3000,http://localhost:4200,http://localhost:8080"

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def resolved_gemini_model(self) -> str:
        model = (self.gemini_model or DEFAULT_GEMINI_MODEL).strip()
        if model in RETIRED_GEMINI_MODELS:
            return DEFAULT_GEMINI_MODEL
        return model or DEFAULT_GEMINI_MODEL


@lru_cache
def get_settings() -> Settings:
    return Settings()
