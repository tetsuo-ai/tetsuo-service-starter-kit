from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Tetsuo Extension API"
    
    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    
    # Scraping Settings
    TETSUO_POOL_ADDRESS: str = "2KB3i5uLKhUcjUwq3poxHpuGGqBWYwtTk5eG9E5WnLG6"
    TETSUO_TOKEN_ADDRESS: str = "8i51XNNpGaKaj4G4nDdmQh95v4FKAxw8mhtaRoKd9tE8"
    
    # Auth Settings
    API_TOKEN: str = "your-secure-token"  # Should be overridden in .env

    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | <cyan>{name}</cyan>:"
        "<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # Monitoring Settings
    MIN_WHALE_USD: float = 1000.0

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
