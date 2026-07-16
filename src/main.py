import os

from dotenv import load_dotenv

load_dotenv()

import time

from connectors import YandexDiskConnector


def fnc_diff_files(dict1, dict2) -> list:
    diff_list = []
    for item in dict1:
        if item not in dict2:
            diff_list.append(item)
    return diff_list


def yandex_delete(files_list: list, ya_disk: YandexDiskConnector) -> None:
    if len(files_list) > 0:
        for fle in files_list:
            ya_disk.delete_file(fle)


def yandex_load(files_list: list, yad: YandexDiskConnector) -> None:
    if len(files_list) > 0:
        for fl in files_list:
            yad.load_file(fl)


def fnc_mtime_files_diff(local_f: dict, yandex_load_f: dict) -> list:
    mtime_fix_files = []
    for nm in local_f:
        if nm in yandex_load_f and local_f[nm] != yandex_load_f[nm]:
            mtime_fix_files.append(nm)
    return mtime_fix_files


def get_local_files(lc_path: str) -> dict:
    lc_files = {}
    for name in os.listdir(lc_path):
        # Полный путь к файлу или папки
        full_path = os.path.join(lc_path, name)
        # Проверяем, что это файл (а не папка)
        if os.path.isfile(full_path):
            lc_files[name] = str(int(os.path.getmtime(full_path)))
    return lc_files


if __name__ == "__main__":
    yandex_disk_files = {}  # файлы на диске Yandex
    local_volume_path = "/home/lenovo/Изображения"

    app_dir = os.path.dirname(os.path.abspath(__file__))
    local_path = os.path.join(app_dir, local_volume_path)

    yandex_disk = YandexDiskConnector()
    yandex_disk.token = os.getenv("YANDEX_TOKEN")
    yandex_disk.yandex_disk_path = os.getenv("YANDEX_DISK_PATH")
    yandex_disk.local_path = local_path

    while True:
        local_files = get_local_files(local_volume_path) # файлы из локальной папки

        if yandex_disk_files != local_files:
            # получение списка файлов из YANDEX DISK
            yandex_disk_files: dict = yandex_disk.info_files() # файлы из локальной папки

            # Запись новых файлов
            upload_files: list = fnc_diff_files(local_files, yandex_disk_files)
            yandex_load(upload_files, yandex_disk)

            # Перезапись измененных файлов на YANDEX DISK
            upload_mtime_files: list = fnc_mtime_files_diff(local_files, yandex_disk_files)
            yandex_load(upload_mtime_files, yandex_disk)

            # Удаление файлов на YANDEX DISK
            delete_files: list = fnc_diff_files(yandex_disk_files, local_files)
            yandex_delete(delete_files, yandex_disk)
        time.sleep(10)
