"""Application settings loaded from environment variables and an optional .env file."""

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration shared by the API, services, and model adapters."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    APP_ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./dev.db"
    RISK_MODEL_TYPE: str = "dummy"
    FLUORIDE_MODEL_PATH: str = "model_artifacts/fluoride/v1/model.joblib"
    BACTERIAL_MODEL_PATH: str = "model_artifacts/bacterial/v1/model.joblib"
    USSD_API_KEY: str | None = None
    USSD_WEBHOOK_SECRET: str | None = None

settings = Settings()
