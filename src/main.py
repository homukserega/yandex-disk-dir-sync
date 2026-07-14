import os

from dotenv import load_dotenv

load_dotenv()

from connectors import YandexDiskConnector

yandex_disk = YandexDiskConnector()

yandex_disk.token = os.getenv("YANDEX_TOKEN")
yandex_disk.yandex_disk_path = os.getenv("YANDEX_DISK_PATH")
yandex_disk.local_path = "/home/lenovo/github-repo/Sevise-files-sync/src"

# yandex_disk.overwrite_existing_file("test_file_to_sync.txt")
