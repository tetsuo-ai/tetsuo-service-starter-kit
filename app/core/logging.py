import sys
from loguru import logger
from app.core.config import get_settings

settings = get_settings()

def setup_logging():
    # Remove default handler
    logger.remove()
    
    # Add console handler with custom format
    logger.add(
        sys.stdout,
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # Add file handler for errors and above
    logger.add(
        "logs/error.log",
        format=settings.LOG_FORMAT,
        level="ERROR",
        rotation="100 MB",
        retention="1 week"
    )
    
    # Add file handler for all logs
    logger.add(
        "logs/app.log",
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        rotation="500 MB",
        retention="1 week"
    )
    
    return logger

# Create logger instance
log = setup_logging()