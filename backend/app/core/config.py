from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> parents[3] is the repo root
ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Security
    SECRET_KEY: str = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    # Database
    DATABASE_URL: str = "postgresql+psycopg://legal:legal@localhost:5433/legal_ai"

    # File storage
    STORAGE_DIR: str = "./storage"
    MAX_UPLOAD_MB: int = 50

    # LLM provider: zai | ollama
    LLM_PROVIDER: str = "zai"
    ZAI_API_KEY: str = ""
    ZAI_BASE_URL: str = "https://api.z.ai/api/paas/v4"
    ZAI_LLM_MODEL: str = "glm-4.6"
    ZAI_EMBED_MODEL: str = "embedding-3"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_LLM_MODEL: str = "llama3.1"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"

    # Must match the embedding model (Z.ai embedding-3 -> 1024, nomic-embed-text -> 768)
    EMBEDDING_DIM: int = 1024

    # RAG tuning
    RETRIEVAL_TOP_K: int = 6
    CHUNK_TOKENS: int = 700
    CHUNK_OVERLAP_TOKENS: int = 100

    @property
    def storage_path(self) -> Path:
        p = Path(self.STORAGE_DIR)
        return p if p.is_absolute() else (ROOT_DIR / p)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
