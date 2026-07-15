import os

from dotenv import load_dotenv

load_dotenv()

from connectors import YandexDiskConnector

yandex_disk = YandexDiskConnector()


def main_fnc(user_path: str):
    app_dir = os.path.dirname(os.path.abspath(__file__))
    local_path = os.path.join(app_dir, user_path)

    yandex_disk.token = os.getenv("YANDEX_TOKEN")
    yandex_disk.yandex_disk_path = os.getenv("YANDEX_DISK_PATH")
    yandex_disk.local_path = local_path


    yandex_disk_files: dict = {}

    local_files = {} # файлы из локальной папки

    for name in os.listdir(local_path):
        # Полный путь к файлу или папки
        full_path = os.path.join(local_path, name)
        # Проверяем, что это файл (а не папка)
        if os.path.isfile(full_path):
            local_files[name] = int(os.path.getmtime(name))

    # if yandex_disk_files != local_files:
    #     # получение списка файлов из YANDEX DISK
    #     yandex_disk_files: dict = yandex_disk.info_files()
    #
    #     # Удаление файлов
    #     yandex_dell_files: list = []
    #     for name in yandex_disk_files:
    #         if name not in local_files:
    #             yandex_dell_files.append(name)
    #
    #     if len(yandex_dell_files) > 0:
    #         for yandex_file in yandex_dell_files:
    #             yandex_disk.delete_file(yandex_file)
    #
    #     # Запись новых файлов
    #     yandex_load_files: list = []
    #     for name in local_files:
    #         if name not in yandex_dell_files:
    #             yandex_load_files.append(name)
    #
    #     if len(yandex_load_files) > 0:
    #         for yandex_file in yandex_load_files:
    #             yandex_disk.load_file(yandex_file)
    #
    #     # Перезапись измененных файлов
    #     yandex_existing_files: list = []
    #     for name in yandex_disk_files:
    #         # сравниваем время изменения - mtime
    #         if local_files[name] != yandex_disk_files[name]:
    #             yandex_disk.load_file(name)


if __name__ == "__main__":
    # user_input_path = input("Please enter the path to your Local Folder:"
    #                         "\nExample: /home/user/Загрузки\n > ")
    main_fnc("/home/lenovo/Изображения")