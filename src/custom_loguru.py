from loguru import logger

import sys

logger_name = "yandex-disk-dir-sync"

app_custom_logger = logger.bind(name=logger_name)

# Удаляем стандартный sink
logger.remove()

# Добавляем вывод в stdout (через sys.stdout)
app_custom_logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss,SSS}</green> <level>{level}</level> <cyan>{message}</cyan>",
    colorize=True,
    level="INFO"
)

# Добавляем файловый sink с ротацией
app_custom_logger.add(
    f"logs/{logger_name}.log",
    rotation="100 MB",
    retention="30 days",
    format="{name} {time:YYYY-MM-DD HH:mm:ss,SSS} {level} {message}",
    level="INFO"
)