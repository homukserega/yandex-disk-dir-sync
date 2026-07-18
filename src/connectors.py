import os

import requests


class YandexDiskConnector:
    def __init__(self):
        self.token = None
        self.yandex_disk_path = None
        self.local_path = None
        self.url = "https://cloud-api.yandex.net/v1/disk/resources"

    def get_headers(self):
        return {
            'Authorization': f'OAuth {self._token}'
        }

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token: str):
        self._token = token

    @property
    def yandex_disk_path(self):
        return self._yandex_disk_path

    @yandex_disk_path.setter
    def yandex_disk_path(self, yandex_disk_path: str):
        """
        :param yandex_disk_path: dir-name-which-will-be-synced on YANDEX DISK
        :return: None
        """
        self._yandex_disk_path = yandex_disk_path

    @property
    def local_path(self):
        return self._local_path

    @local_path.setter
    def local_path(self, local_path: str):
        """
        :param local_path: /home/user/dir-name-which-will-be-synced LOCAL
        :return: None
        """
        self._local_path = local_path

    def upload_file(self, file_name: str) -> None:
        """
        Method Upload single file to Yandex disk_path.
        :param file_name: test_file_to_sync.txt
        :return: None
        """
        # 1. Get href to upload
        yandex_file_path = f"{self._yandex_disk_path}/{file_name}"
        local_file_path = f"{self._local_path}/{file_name}"

        params = {
            'path': yandex_file_path,
            'overwrite': "true",  # можно также 'false' или не указывать
            # 'fields': 'href,method' # опционально – какие поля включить в ответ
        }
        response_get = requests.get(f"{self.url}/upload", params=params, headers=self.get_headers())
        data = response_get.json()
        upload_url = data.get('href')
        # 2. read local file to br uploaded
        with open(local_file_path, "rb") as file:
            requests.put(upload_url, data=file, headers=self.get_headers())

        # 3. Сохраняем исходное время модификации в custom_properties
        mtime = int(os.path.getmtime(local_file_path))  # Unix timestamp
        if not mtime: # если нет времени изменения, оно равно времени создания
            mtime = int(os.path.getctime(local_file_path))
        patch_params = {"path": yandex_file_path}
        patch_data = {
            "custom_properties": {
                "original_mtime": str(mtime)  # Сохраняем как строку
            }
        }
        headers = self.get_headers()
        headers['Content-Type'] = 'application/json'
        requests.patch(
            self.url, params=patch_params, headers=headers, json=patch_data)

    def info_files(self) -> dict:
        """
        Метод для получения фалов в папке Yandex Disk
        :return: dict
        """
        headers = self.get_headers()
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'

        yandex_files = {}
        info_params = {"path": self._yandex_disk_path, "limit": int(10e6)}
        info_response = requests.get(self.url, params=info_params, headers=headers)

        files = info_response.json().get("_embedded", {}).get("items", [])
        for file in files:
            if file["type"] == "file":
                yandex_files[file["name"]] = file.get("custom_properties", {}).get("original_mtime")

        return yandex_files

    def delete_file(self, file_name: str) -> None:
        """
        :param file_name: name of file: str
        :return: None
        """

        headers = self.get_headers()
        params = {
            'path': f"{self.yandex_disk_path}/{file_name}",
            'force_async': "false",  # можно также 'false' или не указывать
            'permanently': "true",
            # 'fields': 'href,method' # опционально – какие поля включить в ответ
        }
        requests.delete(self.url, params=params, headers=headers)
