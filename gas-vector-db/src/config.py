import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 9004
    CHROMA_HOST: str = "gas-rag-technical-chroma"
    CHROMA_PORT: int = 8000
    CHROMA_SSL: bool = False
    DEFAULT_DIMENSION: int = 1536
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
