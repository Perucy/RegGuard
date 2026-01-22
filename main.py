import uvicorn
from src.regguard.core.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "regguard.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level="info",
        reload=settings.ENVIRONMENT == "development"
    )
