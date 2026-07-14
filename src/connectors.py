import os

import requests


# Путь к локальному ПК задается вручную


class YandexDiskConnector:
    def __init__(self):
        self.token = None
        self.yandex_disk_path = None
        self.local_path = None
        self.headers = None

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token: str):
        self._token = token
        self._headers = {
            'Authorization': f'OAuth {self.token}'
        }


    @property
    def yandex_disk_path(self):
        return self._yandex_disk_path

    @yandex_disk_path.setter
    def yandex_disk_path(self, yandex_disk_path: str):
        """
        :param yandex_disk_path: dir-name-which-will-be-synced on YANDEX DISK
        :return:
        """
        self._yandex_disk_path = yandex_disk_path

    @property
    def local_path(self):
        return self._local_path

    @local_path.setter
    def local_path(self, local_path: str):
        """
        :param local_path: /home/user/dir-name-which-will-be-synced LOCAL
        :return: str
        """
        self._local_path = local_path

    def overwrite_existing_file(self, file_name: str):
        """
        Method Upload single file to Yandex disk_path.
        :param file_name: test_file_to_sync.txt
        :return: None
        """
        # 1. Get href to upload
        params = {
            'path': f"{self.yandex_disk_path}/{file_name}",
            'overwrite': "true",  # можно также 'false' или не указывать
            # 'fields': 'href,method' # опционально – какие поля включить в ответ
        }
        response = requests.get(
            "https://cloud-api.yandex.net/v1/disk/resources/upload",
            params=params,
            headers=self._headers,
        )
        data = response.json()
        href = data['href']
        # 2. read local file to br uploaded
        with open(f"{self.local_path}/{file_name}", "r") as file:
            file = file.read()
        # 3. Upload file to Yandex DISK
        response = requests.put(href, data=file, headers=self._headers)
        print(response.status_code)
