from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://nikssec:nikssec@localhost:5432/nikssec"
    SQLITE_URL: str = "sqlite:///./instance/nikssec.db"

    # Security
    SECRET_KEY: str = "change-me-in-production-use-a-real-64-char-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # App
    APP_NAME: str = "Niks Security"
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"
    ENVIRONMENT: str = "development"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Detection engine thresholds
    BRUTE_FORCE_THRESHOLD: int = 5
    BRUTE_FORCE_WINDOW_MIN: int = 10
    PORT_SCAN_THRESHOLD: int = 15
    PORT_SCAN_WINDOW_MIN: int = 5
    DDOS_REQUEST_THRESHOLD: int = 100
    DDOS_WINDOW_SEC: int = 60

    # File uploads
    MAX_UPLOAD_SIZE: int = 20 * 1024 * 1024  # 20MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: str = "log,txt,csv,json"

    # AI Copilot
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:0.5b"
    AI_PROVIDER: str = "ollama"
    COPILOT_ENABLED: bool = True
    COPILOT_MAX_TOKENS: int = 4096
    COPILOT_TIMEOUT: int = 120

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
