import requests

class FileSyncError(Exception):
    """Исключение, содержащее имя файла и исходную ошибку."""
    def __init__(self, filename: str, original_exception: Exception):
        self.filename = filename
        self.original_exception = original_exception
        super().__init__(
            f"Синхронизация файла '{filename}' "
            f"не удалась: {original_exception}"
        )


def map_error_type(exception: Exception) -> str:
    """Возвращает читаемое описание типа ошибки."""
    if isinstance(exception, requests.RequestException):
        return "Ошибка сетевого соединения."
    if isinstance(exception, FileNotFoundError):
        return "Файл не найден"
    if isinstance(exception, PermissionError):
        return "Недостаточно прав для чтения файла."
    if isinstance(exception, OSError):
        return "Ошибка файловой системы."
    if isinstance(exception, ValueError):
        return "Ошибка получения ссылки для загрузки."
    if exception.args[0] == "Не удалось получить ссылку для загрузки (возможно, неверный токен)":
            return f"{exception}"
    return f"Неизвестная ошибка ({type(exception).__name__})"


class UnauthorizedError(BaseException):
    pass