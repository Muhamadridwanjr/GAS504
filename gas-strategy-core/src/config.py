import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    STRATEGY_PATH: str = os.getenv("STRATEGY_PATH", "./strategies")
    STRATEGY_DB_URL: str = os.getenv("STRATEGY_DB_URL", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    RAG_MACRO_URL: str = os.getenv("RAG_MACRO_URL", "http://gas-rag-macro:9002")
    RAG_TECHNICAL_URL: str = os.getenv("RAG_TECHNICAL_URL", "http://gas-rag-technical:9001")
    
settings = Settings()
