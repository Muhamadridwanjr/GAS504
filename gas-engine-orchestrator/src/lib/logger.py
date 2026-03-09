import sys
from loguru import logger
from .config import settings

def setup_logger():
    # Remove default handler
    logger.remove()
    
    # Set log level based on environment config
    log_level = settings.log_level.upper()
    
    # Add console handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
    )
    
    return logger

log = setup_logger()
