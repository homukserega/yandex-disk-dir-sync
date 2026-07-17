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
        for item in files_list:
            ya_disk.delete_file(item)


def yandex_upload(files_list: list, yad: YandexDiskConnector) -> None:
    if len(files_list) > 0:
        for item in files_list:
            yad.upload_file(item)


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
            # получение списка файлов из YANDEX DISK
            yandex_disk_files: dict = yandex_disk.info_files()

            # Удаление файлов на YANDEX DISK
            delete_files: list = fnc_diff_files(yandex_disk_files, local_files)
            yandex_delete(delete_files, yandex_disk)

            # Запись новых файлов на YANDEX DISK
            upload_files: list = fnc_diff_files(local_files, yandex_disk_files)
            yandex_upload(upload_files, yandex_disk)

            # Перезапись измененных файлов на YANDEX DISK
            upload_mtime_files: list = fnc_mtime_files_diff(local_files, yandex_disk_files)
            yandex_upload(upload_mtime_files, yandex_disk)
        time.sleep(10)
