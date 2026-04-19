from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Business Rules
    TOLERANCE_TOTALS: float = 0.5
    TOLERANCE_LINEITEMS: float = 1.0
    
    # Supported Currencies
    SUPPORTED_CURRENCIES: list[str] = ["EUR", "USD", "GBP", "INR"]
    
    # Server Config
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
