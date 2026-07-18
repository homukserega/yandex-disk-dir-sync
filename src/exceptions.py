import requests

class FileSyncError(Exception):
    """Исключение, содержащее имя файла и исходную ошибку."""
    def __init__(self, filename: str, original_exception: Exception):
        self.filename = filename
        self.original_exception = original_exception
        super().__init__(f"Синхронизация файла '{filename}' не удалась: {original_exception}")


def map_error_type(exception: Exception) -> str:
    """Возвращает читаемое описание типа ошибки."""
    if isinstance(exception, requests.RequestException):
        return "Ошибка соединения"
    if isinstance(exception, FileNotFoundError):
        return "Файл не найден"
    if isinstance(exception, PermissionError):
        return "Недостаточно прав для чтения файла"
    if isinstance(exception, OSError):
        return "Ошибка файловой системы"
    if isinstance(exception, ValueError):
        return "Ошибка получения ссылки для загрузки"
    return f"Неизвестная ошибка ({type(exception).__name__})"