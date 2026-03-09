import json
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 9502
    environment: str = "development"
    log_level: str = "INFO"

    redis_url: str = "redis://localhost:6379"
    market_data_url: str = "http://gas-feature-engine:9499"
    
    # We load default pairs as JSON string and parse it
    default_pairs: str = '[["XAUUSD","DXY"],["EURUSD","GBPUSD"]]'
    
    zscore_threshold: float = 2.0
    lookback_period: int = 20
    update_interval: int = 3600

    @property
    def parsed_pairs(self):
        try:
            return json.loads(self.default_pairs)
        except:
            return [["XAUUSD","DXY"]]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
