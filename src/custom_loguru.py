from loguru import logger

import sys

logger_name = "synchronizer"

app_custom_logger = logger.bind(name=logger_name)

# Удаляем стандартный sink
app_custom_logger.remove(0)

# Добавляем вывод в stdout (через sys.stdout)
app_custom_logger.add(
    sys.stdout,
    format="<green>{time}</green> | <level>{level}</level> | <cyan>{message}</cyan>",
    colorize=True,
    level="DEBUG"
)

# Добавляем файловый sink с ротацией
app_custom_logger.add(
    f"logs/{logger_name}.log",
    rotation="100 MB",
    retention="30 days",
    format="{time} | {level} | {message}",
    level="INFO"
)