import logging
from src.config import settings

def setup_logger(name: str) -> logging.Logger:
    """Konfigurasi logger standar untuk service."""
    logger = logging.getLogger(name)
    
    # Konversi str log_level (dari env) ke logging log level (int)
    level_name = settings.log_level.upper()
    level = logging.getLevelName(level_name)
    if not isinstance(level, int):
        level = logging.INFO
        
    logger.setLevel(level)
    
    # Hindari menambahkan handler berulang
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
