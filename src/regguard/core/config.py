""" Config management using environment variable """
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """ App settings loaded from env variables """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Api keys
    ANTHROPIC_API_KEY: str

    # LANGSMITH
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_TRACING: bool = False
    LANGSMITH_PROJECT: str = "regguard-dev"

settings = Settings()