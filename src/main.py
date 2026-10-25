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
                start_time = time.time()
                yad.upload_file(item)
                tot_time = time.time() - start_time
                app_custom_logger.info(f"Файл '{item}' успешно {action} за {tot_time}!")
            except FileSyncError as exc:
                error_desc = map_error_type(exc.original_exception)
                app_custom_logger.error(
                    f"Файл '{exc.filename}' не был {action}. {error_desc}"
                )


def add_local_mtime_files_to_upload(local_f: dict, yandex_load_f: dict) -> list:
    """
    Возвращает список файлов, которые есть и локально, и на Диске,
    но у которых отличается mtime.

    Файлы с неизвестным mtime на Диске (None) пропускаются:
    мы не можем определить, изменились ли они, а перезаливать
    каждый цикл — значит устроить бесконечную перезакачку.
    Для «догона» таких файлов используйте FULL_RESYNC=true.
    """
    mtime_fix_files = []
    for f_name, local_mtime in local_f.items():
        if f_name not in yandex_load_f:
            continue
        yandex_mtime = yandex_load_f[f_name]
        if yandex_mtime is None:
            app_custom_logger.warning(
                f"Файл '{f_name}': mtime на Яндекс.Диске неизвестен, "
                f"пропускаем сравнение. Используйте FULL_RESYNC=true, "
                f"чтобы перезалить."
            )
            continue
        if local_mtime != yandex_mtime:
            mtime_fix_files.append(f_name)
    return mtime_fix_files


def get_local_files(local_path: str) -> dict:
    loc_files = {}
    for root, _dirs, files in os.walk(local_path):
        for name in files:
            full_path = os.path.join(root, name)
            if os.path.islink(full_path):
                continue
            rel = os.path.relpath(full_path, local_path).replace(os.sep, "/")
            loc_files[rel] = str(int(os.path.getmtime(full_path)))
    return loc_files


def sync_once(
        yandex_disk: YandexDiskConnector,
        yandex_disk_files: dict,
        local_volume_path: str,
) -> dict:
    """Один цикл синхронизации. Возвращает актуальное состояние Диска."""
    local_files = get_local_files(local_volume_path)

    if yandex_disk_files == local_files:
        return yandex_disk_files

    delete_files = fnc_diff_files(yandex_disk_files, local_files)
    upload_files = fnc_diff_files(local_files, yandex_disk_files)
    upload_mtime_files = add_local_mtime_files_to_upload(
        local_files, yandex_disk_files
    )

    if not (delete_files or upload_files or upload_mtime_files):
        # Расхождение есть, но действовать не на что
        # (например, None mtime без FULL_RESYNC).
        return yandex_disk_files

    yandex_delete(delete_files, yandex_disk, action="удален")
    if delete_files:
        yandex_disk.cleanup_empty_dirs(delete_files)
    yandex_upload(upload_files, yandex_disk, action="загружен")
    yandex_upload(upload_mtime_files, yandex_disk, action="перезаписан")

    yandex_disk_files = yandex_disk.info_files()
    app_custom_logger.info(
        f"Файлы из Yandex Disk: "
        f"'{yandex_disk.yandex_disk_path}' успешно получены"
    )
    return yandex_disk_files


if __name__ == "__main__":
    local_volume_path = "data"
    yandex_disk_files: dict = {}

    yandex_disk = YandexDiskConnector()
    yandex_disk.local_path = local_volume_path
    yandex_disk.token = os.getenv("YANDEX_TOKEN")
    yandex_disk.yandex_disk_path = os.getenv("YANDEX_DISK_PATH")

    app_custom_logger.info(
        f"Программа синхронизации файлов начинает работу с директорией "
        f"{os.getenv('HOST_PATH')}."
    )

    full_resync = os.getenv("FULL_RESYNC", "false").lower() in (
        "1", "true", "yes", "on",
    )

    try:
        if full_resync:
            app_custom_logger.warning(
                "FULL_RESYNC=true — удаляю всё содержимое "
                f"'{yandex_disk.yandex_disk_path}' на Яндекс.Диске "
                "и заливаю локальные файлы заново."
            )
            yandex_disk.clear_disk_dir()
            yandex_disk_files = {}
            app_custom_logger.info(
                f"Каталог '{yandex_disk.yandex_disk_path}' очищен."
            )
        else:
            yandex_disk_files = yandex_disk.info_files()
            app_custom_logger.info(
                f"Файлы из Yandex Disk '{yandex_disk.yandex_disk_path}' "
                f"успешно получены."
            )
    except UnauthorizedError as e:
        app_custom_logger.error(f"Ошибка авторизации: {e}")
    except FileNotFoundError:
        try:
            yandex_disk._ensure_folder(yandex_disk.yandex_disk_path)
            yandex_disk_files = {}
            app_custom_logger.info(
                f"Каталог '{yandex_disk.yandex_disk_path}' создан на Яндекс.Диске."
            )
        except requests.RequestException as e:
            app_custom_logger.error(f"Не удалось создать каталог на Диске: {e}")
    except requests.RequestException as e:
        app_custom_logger.error(f"Ошибка при первичном обращении к API: {e}")

    while True:
        try:
            yandex_disk_files = sync_once(
                yandex_disk, yandex_disk_files, local_volume_path
            )
        except UnauthorizedError:
            app_custom_logger.error(
                "Ошибка авторизации, проверьте валидность вашего токена."
            )
        except FileNotFoundError as e:
            app_custom_logger.error(f"Ошибка: {e}")
        except requests.RequestException as e:
            app_custom_logger.error(f"Ошибка сетевого соединения: {e}")
        except Exception as e:
            app_custom_logger.error(f"Неожиданная ошибка: {e}")

        time.sleep(10)
