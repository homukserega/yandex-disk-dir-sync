import os
import time
import requests

from exceptions import FileSyncError, UnauthorizedError


class YandexDiskConnector:
    def __init__(self):
        self.chunk_size = 1024 * 8
        self.token = None
        self.yandex_disk_path = None
        self.local_path = None
        self.url = "https://cloud-api.yandex.net/v1/disk/resources"
        self._ensured_folders: set[str] = set()

    def get_headers(self):
        return {"Authorization": f"OAuth {self._token}"}

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

    def chunked_reader(self, file_path: str):
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk

    def _ensure_folder(self, full_path: str) -> None:
        if full_path in self._ensured_folders:
            return
        headers = self.get_headers()
        r = requests.get(self.url, params={"path": full_path}, headers=headers)
        if r.status_code == 200:
            if r.json().get("type") != "dir":
                raise requests.RequestException(
                    f"Путь '{full_path}' существует, но это не папка."
                )
            self._ensured_folders.add(full_path)
            return
        if r.status_code == 404:
            put = requests.put(
                self.url, params={"path": full_path}, headers=headers
            )
            if put.status_code not in (201, 409):
                raise requests.RequestException(
                    f"Не удалось создать папку '{full_path}': "
                    f"{put.status_code} - {put.text[:200]}"
                )
            self._ensured_folders.add(full_path)
            return
        raise requests.RequestException(
            f"Ошибка API Яндекс.Диска: {r.status_code} - {r.text[:200]}"
        )

    def _ensure_folder_path(self, relative_dir: str) -> None:
        self._ensure_folder(self._yandex_disk_path)
        if not relative_dir:
            return
        current = self._yandex_disk_path
        for part in [p for p in relative_dir.split("/") if p]:
            current = f"{current}/{part}"
            self._ensure_folder(current)

    def upload_file(self, file_name: str) -> None:
        """
        Upload single file to Yandex disk_path.
        :param file_name: relative path like 'sub/dir/file.txt'
        """
        try:
            yandex_file_path = f"{self._yandex_disk_path}/{file_name}"
            local_file_path = os.path.join(self._local_path, file_name)

            parent = os.path.dirname(file_name).replace(os.sep, "/")
            self._ensure_folder_path(parent)

            params = {
                "path": yandex_file_path,
                "overwrite": "true",
            }

            response_get = requests.get(
                f"{self.url}/upload", params=params, headers=self.get_headers()
            )

            # ---- Обработка 409 DiskPathDoesntExistsError ----
            if response_get.status_code == 409:
                try:
                    err = response_get.json()
                except ValueError:
                    err = {}
                if err.get("error") == "DiskPathDoesntExistsError":
                    # Кэш мог устареть (например, после FULL_RESYNC).
                    # Сбрасываем его для родительских папок и создаём их заново.
                    self._ensured_folders.clear()  # проще всего сбросить весь кэш
                    self._ensure_folder_path(parent)
                    # Повторяем запрос на получение upload-ссылки
                    response_get = requests.get(
                        f"{self.url}/upload", params=params, headers=self.get_headers()
                    )
                else:
                    raise FileSyncError(
                        file_name,
                        requests.RequestException(
                            f"GET /upload вернул 409: {response_get.text[:200]}"
                        ),
                    )
            # ------------------------------------------------

            if response_get.status_code == 401:
                raise UnauthorizedError(
                    "Ошибка авторизации при получении upload-ссылки."
                )
            if response_get.status_code != 200:
                raise FileSyncError(
                    file_name,
                    requests.RequestException(
                        f"GET /upload вернул {response_get.status_code}: "
                        f"{response_get.text[:200]}"
                    ),
                )

            data = response_get.json()
            upload_url = data.get("href")
            if not upload_url:
                raise FileSyncError(
                    file_name,
                    requests.RequestException(f"Пустой href в ответе upload: {data}"),
                )

            file_size_bytes = os.path.getsize(local_file_path)
            if file_size_bytes <= 10 * 1024 * 1024:
                with open(local_file_path, "rb") as f:
                    payload = f.read()
            else:
                payload = self.chunked_reader(local_file_path)

            put_r = requests.put(upload_url, data=payload, headers=self.get_headers())
            if put_r.status_code not in (200, 201, 202, 204):
                raise FileSyncError(
                    file_name,
                    requests.RequestException(
                        f"PUT вернул {put_r.status_code}: {put_r.text[:200]}"
                    ),
                )

            mtime = int(os.path.getmtime(local_file_path))
            patch_params = {"path": yandex_file_path}
            patch_data = {"custom_properties": {"original_mtime": str(mtime)}}

            headers = self.get_headers()
            headers["Content-Type"] = "application/json"

            patch_r = requests.patch(
                self.url, params=patch_params, headers=headers, json=patch_data
            )
            if patch_r.status_code != 200:
                raise FileSyncError(
                    file_name,
                    requests.RequestException(
                        f"PATCH mtime вернул {patch_r.status_code}: "
                        f"{patch_r.text[:200]}"
                    ),
                )

        except (
                requests.RequestException,
                ValueError,
                KeyError,
                PermissionError,
                OSError,
                FileNotFoundError,
        ) as exception:
            raise FileSyncError(file_name, exception)

    def _list_folder(self, disk_path: str) -> list:
        """Все непосредственные дети disk_path (файлы + каталоги), с пагинацией."""
        headers = self.get_headers()
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"

        items, offset, limit = [], 0, 1000
        while True:
            params = {
                "path": disk_path,
                "limit": limit,
                "offset": offset,
                "fields": "name,type,custom_properties",
            }
            r = requests.get(self.url, params=params, headers=headers)

            if r.status_code == 401:
                raise UnauthorizedError("Ошибка авторизации. Проверьте ваш ТОКЕН.")
            if r.status_code == 404:
                raise FileNotFoundError(
                    f"Каталог '{disk_path}' не найден на Яндекс.Диске."
                )
            if r.status_code != 200:
                raise requests.RequestException(
                    f"Ошибка API Яндекс.Диска: {r.status_code} - {r.text[:200]}"
                )

            embedded = r.json().get("_embedded", {})
            batch = embedded.get("items", [])
            items.extend(batch)
            offset += len(batch)
            if not batch or offset >= embedded.get("total", 0):
                break
        return items

    def _collect_files(self, disk_path: str, prefix: str, result: dict) -> None:
        for item in self._list_folder(disk_path):
            rel = f"{prefix}/{item['name']}" if prefix else item["name"]
            if item["type"] == "file":
                mtime = item.get("custom_properties", {}).get("original_mtime")
                result[rel] = str(mtime) if mtime not in (None, "") else None
            elif item["type"] == "dir":
                self._collect_files(f"{disk_path}/{item['name']}", rel, result)

    def info_files(self) -> dict:
        yandex_files: dict = {}
        self._collect_files(self._yandex_disk_path, "", yandex_files)
        return yandex_files

    def delete_file(self, file_name: str) -> None:
        try:
            headers = self.get_headers()
            params = {
                "path": f"{self._yandex_disk_path}/{file_name}",
                "force_async": "false",
                "permanently": "true",
            }
            r = requests.delete(self.url, params=params, headers=headers)
            if r.status_code == 401:
                raise UnauthorizedError("Ошибка авторизации при удалении.")
            if r.status_code == 404:
                return
            if r.status_code not in (200, 202, 204):
                raise requests.RequestException(
                    f"Удаление '{file_name}' не удалось: "
                    f"{r.status_code} - {r.text[:200]}"
                )
        except (
                requests.RequestException,
                ValueError,
                PermissionError,
                OSError,
                FileNotFoundError,
        ) as exception:
            raise FileSyncError(file_name, exception)

    def cleanup_empty_dirs(self, deleted_files: list) -> None:
        """
        Удаляет опустевшие родительские каталоги после удаления файлов.
        Идём от самых глубоких к самым верхним, чтобы удалить всю цепочку.
        """
        parents: set[str] = set()
        for f in deleted_files:
            parent_rel = os.path.dirname(f).replace(os.sep, "/")
            while parent_rel:
                parents.add(f"{self._yandex_disk_path}/{parent_rel}")
                parent_rel = os.path.dirname(parent_rel).replace(os.sep, "/")

        for path in sorted(parents, key=lambda p: p.count("/"), reverse=True):
            try:
                if self._list_folder(path):
                    continue
            except FileNotFoundError:
                continue
            except requests.RequestException:
                continue
            try:
                requests.delete(
                    self.url,
                    params={"path": path, "permanently": "true"},
                    headers=self.get_headers(),
                )
            except requests.RequestException:
                pass

    def clear_disk_dir(self, max_retries: int = 5, base_delay: float = 2.0) -> None:
        """
        Полностью удаляет YANDEX_DISK_PATH со всем содержимым
        и создаёт пустую папку заново.

        При ошибке 423 (ресурс заблокирован) делает несколько попыток
        с экспоненциально растущей паузой.
        """
        headers = self.get_headers()
        for attempt in range(1, max_retries + 1):
            r = requests.delete(
                self.url,
                params={"path": self._yandex_disk_path, "permanently": "true"},
                headers=headers,
            )

            if r.status_code in (200, 202, 204, 404):
                # Удаление запущено, уже удалено или папки не было — успех.
                self._ensured_folders.clear()
                self._ensure_folder(self._yandex_disk_path)
                return

            if r.status_code == 423:
                if attempt == max_retries:
                    raise requests.RequestException(
                        f"Ресурс '{self._yandex_disk_path}' остаётся заблокированным "
                        f"после {max_retries} попыток. "
                        f"Убедитесь, что никакие другие процессы не используют эту папку."
                    )
                delay = base_delay * (2 ** (attempt - 1))
                # Здесь можно добавить логирование, если есть доступ к логгеру
                # app_custom_logger.warning(
                #     f"Попытка {attempt}/{max_retries}: ресурс заблокирован, "
                #     f"повтор через {delay:.1f} сек."
                # )
                time.sleep(delay)
                continue

            if r.status_code == 401:
                raise UnauthorizedError("Ошибка авторизации при очистке Диска.")

            raise requests.RequestException(
                f"Не удалось очистить '{self._yandex_disk_path}': "
                f"{r.status_code} - {r.text[:200]}"
            )
