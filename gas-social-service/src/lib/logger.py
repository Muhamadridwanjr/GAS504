import logging
import sys
from src.config import settings


def get_logger(name: str = "gas-social-service") -> logging.Logger:
    log = logging.getLogger(name)
    if not log.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        log.addHandler(handler)
    log.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    return log


logger = get_logger()
