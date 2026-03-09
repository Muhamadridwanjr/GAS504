import logging, sys
from src.config import settings

def setup_logger():
    logger = logging.getLogger("gas_terminal_service")
    level = logging.getLevelName(settings.log_level.upper())
    logger.setLevel(level)
    if not logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(level)
        h.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(h)
    return logger

logger = setup_logger()
