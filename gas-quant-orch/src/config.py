from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 9500
    environment: str = "development"
    log_level: str = "INFO"

    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 5
    
    feature_engine_url: str = "http://gas-feature-engine:9499"
    regime_detector_url: str = "http://gas-regime-detector:9503"
    pattern_detector_url: str = "http://gas-pattern-detector:9501"
    statarb_engine_url: str = "http://gas-statarb-engine:9502"
    trend_engine_url: str = "http://gas-trend-engine:9513"
    market_phase_url: str = "http://gas-market-phase:9510"
    orderflow_url: str = "http://gas-orderflow:9514"

    request_timeout: float = 2.0
    signal_threshold: float = 0.5

    weight_regime: float = 1.0
    weight_pattern: float = 1.5
    weight_statarb: float = 1.0
    weight_trend: float = 1.2
    weight_phase: float = 0.8
    weight_orderflow: float = 1.0

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
