import os

import requests
from dotenv import load_dotenv

load_dotenv()


# Путь к локальному ПК задается вручную


class YandexDisk:
    def __init__(self):
        self.token = os.getenv('YANDEX_TOKEN')
        self.url_to_upload = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        self.yandex_disk_path = os.getenv('YANDEX_DISK_PATH')

    def upload_file_to_yandex(self, local_file_path, file_name):
        """
        Method Upload a file to Yandex.
        :param local_file_path:
        :param file_name:
        :return: None
        """
        # 1. Get href to upload
        params = {
            'path': self.yandex_disk_path,
            'overwrite': "true",  # можно также 'false' или не указывать
            # 'fields': 'href,method' # опционально – какие поля включить в ответ
        }
        headers = {
            'Authorization': f'OAuth {self.token}'
        }
        response = requests.get(self.url_to_upload, params=params, headers=headers)
        data = response.json()
        href = data['href']
        # 2. read local file to br uploaded
        with open(f"{local_file_path}/{file_name}", "r") as file:
            file = file.read()
        # 3. Upload file to Yandex DISK
        response = requests.put(href, data=file, headers=headers)
        print(response.status_code, response.json())
