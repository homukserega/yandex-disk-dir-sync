from dotenv import load_dotenv

from loguru import logger

import os

import requests

import sys

import time

from connectors import YandexDiskConnector

load_dotenv()

# Удаляем стандартный sink
logger.remove(0)

# Добавляем вывод в stdout (через sys.stdout)
logger.add(
    sys.stdout,
    format="<green>{time}</green> | <level>{level}</level> | <cyan>{message}</cyan>",
    colorize=True,
    level="DEBUG"
)

# Добавляем файловый sink с ротацией
logger.add(
    "logs/Service-files-sync.log",
    rotation="100 MB",
    retention="30 days",
    format="{time} | {level} | {message}",
    level="INFO"
)


class FileSyncError(Exception):
    """Исключение, содержащее имя файла и исходную ошибку."""
    def __init__(self, filename: str, original_exception: Exception):
        self.filename = filename
        self.original_exception = original_exception
        super().__init__(f"Синхронизация файла '{filename}' не удалась: {original_exception}")


def map_error_type(exception: Exception) -> str:
    """Возвращает читаемое описание типа ошибки."""
    if isinstance(exception, requests.RequestException):
        return "Ошибка соединения"
    if isinstance(exception, FileNotFoundError):
        return "Файл не найден"
    if isinstance(exception, PermissionError):
        return "Недостаточно прав для чтения файла"
    if isinstance(exception, OSError):
        return "Ошибка файловой системы"
    if isinstance(exception, ValueError):
        return "Ошибка получения ссылки для загрузки"
    return f"Неизвестная ошибка ({type(exception).__name__})"


def fnc_diff_files(local_f: dict, yandex_load_f: dict) -> list:
    return [f for f in local_f if f not in yandex_load_f]


def yandex_delete(files_list: list, ya_disk: YandexDiskConnector , action: str) -> None:
    if len(files_list) > 0:
        for item in files_list:
            try:
                ya_disk.delete_file(item)
                logger.info(f"Файл '{item}' успешно {action}!")
            except FileSyncError as e:
                error_desc = map_error_type(e.original_exception)
                logger.error(
                    f"Файл '{e.filename}' не был {action}. {error_desc}: {e.original_exception}"
                )

def yandex_upload(files_list: list, yad: YandexDiskConnector, action: str) -> None:
    if len(files_list) > 0:
        for item in files_list:
            try:
                yad.upload_file(item)
                logger.info(f"Файл '{item}' успешно {action}!")
            except FileSyncError as e:
                error_desc = map_error_type(e.original_exception)
                logger.error(
                    f"Файл '{e.filename}' не был {action}. {error_desc}: {e.original_exception}"
                )


def fnc_mtime_files_diff(local_f: dict, yandex_load_f: dict) -> list:
    mtime_fix_files = []
    for f_name in local_f:
        if f_name in yandex_load_f and local_f[f_name] != yandex_load_f[f_name]:
            mtime_fix_files.append(f_name)
    return mtime_fix_files


def get_local_files(local_path: str) -> dict:
    loc_files = {}
    for name in os.listdir(local_path):
        # Полный путь к файлу или папки
        full_path = os.path.join(local_path, name)
        # Проверяем, что это файл (а не папка)
        if os.path.isfile(full_path):
            loc_files[name] = str(int(os.path.getmtime(full_path)))
    return loc_files


if __name__ == "__main__":
    local_volume_path = "data"

    yandex_disk = YandexDiskConnector()
    yandex_disk.token = os.getenv("YANDEX_TOKEN")
    yandex_disk.yandex_disk_path = os.getenv("YANDEX_DISK_PATH")
    yandex_disk.local_path = local_volume_path

    # получение списка файлов из YANDEX DISK
    yandex_disk_files: dict = yandex_disk.info_files()

    while True:
        # получение списка файлов из локальной папки
        local_files = get_local_files(local_volume_path)

        if yandex_disk_files != local_files:
            # Удаление файлов на YANDEX DISK
            delete_files: list = fnc_diff_files(yandex_disk_files, local_files)
            yandex_delete(delete_files, yandex_disk, action="удален")

            # Запись новых файлов на YANDEX DISK
            upload_files: list = fnc_diff_files(local_files, yandex_disk_files)
            yandex_upload(upload_files, yandex_disk, action="загружен")

            # Перезапись измененных файлов на YANDEX DISK
            upload_mtime_files: list = fnc_mtime_files_diff(local_files, yandex_disk_files)
            yandex_upload(upload_mtime_files, yandex_disk, action="перезаписан")

            # получение списка файлов из YANDEX DISK
            yandex_disk_files: dict = yandex_disk.info_files()
        time.sleep(10)
