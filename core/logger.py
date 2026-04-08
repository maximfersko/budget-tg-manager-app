import logging
import sys

from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO"
)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        level = logger.level(record.levelname).name if record.levelname in logger._core.levels else record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=0)
