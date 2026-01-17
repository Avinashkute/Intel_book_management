import logging
import sys
from app.core.config import get_settings

settings = get_settings()


def setup_logging():
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log")
        ]
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
