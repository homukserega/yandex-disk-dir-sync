import os
import time

import requests
from dotenv import load_dotenv

from connectors import YandexDiskConnector
from custom_loguru import app_custom_logger
from exceptions import FileSyncError, UnauthorizedError, map_error_type

load_dotenv()


def fnc_diff_files(local_f: dict, yandex_load_f: dict) -> list:
    return [f for f in local_f if f not in yandex_load_f]


def yandex_delete(files: list, ya_disk: YandexDiskConnector, action: str) -> None:
    if len(files) > 0:
        for item in files:
            try:
                ya_disk.delete_file(item)
                app_custom_logger.info(f"Файл '{item}' успешно {action}!")
            except FileSyncError as ex:
                error_desc = map_error_type(ex.original_exception)
                app_custom_logger.error(
                    f"Файл '{ex.filename}' не был {action}. {error_desc}"
                )


def yandex_upload(files: list, yad: YandexDiskConnector, action: str) -> None:
    if len(files) > 0:
        for item in files:
            try:
                yad.upload_file(item)
                app_custom_logger.info(f"Файл '{item}' успешно {action}!")
            except FileSyncError as exc:
                error_desc = map_error_type(exc.original_exception)
                app_custom_logger.error(
                    f"Файл '{exc.filename}' не был {action}. {error_desc}"
                )


def add_local_mtime_files_to_upload(local_f: dict, yandex_load_f: dict) -> list:
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
    yandex_disk_files = {}

    yandex_disk = YandexDiskConnector()
    yandex_disk.local_path = local_volume_path

    yandex_disk.token = os.getenv("YANDEX_TOKEN")
    yandex_disk.yandex_disk_path = os.getenv("YANDEX_DISK_PATH")
    app_custom_logger.info(
        f"Программа синхронизации файлов начинает работу с директорией "
        f"{os.getenv('HOST_PATH')}."
    )
    try:
        # Первое получение списка файлов – если здесь ошибка, программа завершится с логом
        yandex_disk_files = yandex_disk.info_files()
        app_custom_logger.info(
            f"Файлы из Yandex Disk '{yandex_disk.yandex_disk_path}' успешно получены."
        )
    except UnauthorizedError as e:
        app_custom_logger.error(f"Ошибка авторизации: {e}")
    except FileNotFoundError as e:
        app_custom_logger.error(f"Ошибка: {e}")
    except requests.RequestException:
        app_custom_logger.error("Ошибка сетевого соединения.")

    while True:
        try:
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
                upload_mtime_files: list = add_local_mtime_files_to_upload(
                    local_files, yandex_disk_files
                )
                yandex_upload(upload_mtime_files, yandex_disk, action="перезаписан")

                # получение списка файлов из YANDEX DISK
                yandex_disk_files = yandex_disk.info_files()
                app_custom_logger.info(
                    f"Файлы из Yandex Disk: "
                    f"'{yandex_disk.yandex_disk_path}' успешно получены"
                )
        except UnauthorizedError:
            app_custom_logger.error(
                "Ошибка авторизации проверьте валидность вашего токена"
            )
        except FileNotFoundError as e:
            app_custom_logger.error(f"Ошибка: {e}")
        except requests.RequestException:
            app_custom_logger.error("Ошибка сетевого соединения.")
        except Exception as e:
            app_custom_logger.error(f"Неожиданная ошибка: {e}")

        time.sleep(10)
