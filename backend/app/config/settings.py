import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None
    gemini_model: str
    gcp_project_id: str | None
    google_application_credentials: str | None
    environment: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        gcp_project_id=os.getenv("GCP_PROJECT_ID"),
        google_application_credentials=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        environment=os.getenv("ENVIRONMENT", "development"),
    )
