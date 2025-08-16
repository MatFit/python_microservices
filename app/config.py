from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict

# Folder containing config.py
BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    # Auto searches for .env
    gemini_api_key: str = Field(...)
    gemini_base_url: str = Field(...)
    gemini_model: str   = Field(...)

    # Alpaca does not require base url only needs alpaca_py package
    alpaca_api_key: str = Field(...)
    alpaca_secret_key: str = Field(...)

    news_api_key: str = Field(...)
    news_base_url: str = Field(...)

    news_everything_url: str = Field(...)
    news_headlines_url: str = Field(...)

    # Parameters
    max_tokens: int = 1000
    temperature: float  = 0.7

    # Config in dictionary
    model_config = ConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", case_sensitive=False, extra="forbid")

settings = Settings()
