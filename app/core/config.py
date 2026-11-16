from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ClinicFlow API"
    VERSION: str = "1.0.0"

    # Güvenlik Ayarları
    SECRET_KEY: str = "clinicflow-super-secret-key-2026-production-ready"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 Gün (1440 Dakika)

    DATABASE_URL: str = "sqlite:///./clinicflow.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
