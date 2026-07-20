import sys

from loguru import logger

logger_name = "ya-disk-sync"

app_custom_logger = logger.bind(name=logger_name)

# Удаляем стандартный sink
logger.remove()

# Добавляем вывод в stdout (через sys.stdout)
app_custom_logger.add(
    sys.stdout,
    format="{extra[name]} <green>{time:YYYY-MM-DD HH:mm:ss,SSS}</green> <level>{level}</level> <cyan>{message}</cyan>",
    colorize=True,
    level="INFO",
)

# Добавляем файловый sink с ротацией
app_custom_logger.add(
    f"logs/{logger_name}.log",
    rotation="100 MB",
    retention="30 days",
    format="{extra[name]} {time:YYYY-MM-DD HH:mm:ss,SSS} {level} {message}",
    level="INFO",
)
