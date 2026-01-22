""" Config management using environment variable """
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """ App settings loaded from env variables """

    # Application settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Api keys
    ANTHROPIC_API_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()