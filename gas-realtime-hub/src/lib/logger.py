import logging
import sys
from src.config import settings

def setup_logger():
    logger = logging.getLogger("gas_realtime_hub")
    
    level = logging.getLevelName(settings.log_level.upper())
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

logger = setup_logger()
