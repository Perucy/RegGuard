""" Config management using environment variable """
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """ App settings loaded from env variables """

    # Application settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Api keys
    ANTHROPIC_API_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()