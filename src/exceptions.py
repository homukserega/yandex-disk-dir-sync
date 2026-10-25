import requests


class FileSyncError(Exception):
    """Исключение, содержащее имя файла и исходную ошибку."""

    def __init__(self, filename: str, original_exception: Exception):
        self.filename = filename
        self.original_exception = original_exception
        super().__init__(
            f"Синхронизация файла '{filename}' не удалась: {original_exception}"
        )


def map_error_type(exception: Exception) -> str:
    """Возвращает читаемое описание типа ошибки."""
    if isinstance(exception, requests.RequestException):
        msg = str(exception) or ""
        if msg and not msg.lower().startswith(
                ("connection", "read timed out", "max retries")
        ):
            return msg
        return "Ошибка сетевого соединения."
    if isinstance(exception, FileNotFoundError):
        return "Файл не найден"
    if isinstance(exception, PermissionError):
        return "Недостаточно прав для чтения файла."
    if isinstance(exception, OSError):
        return "Ошибка файловой системы."
    if isinstance(exception, ValueError):
        return "Ошибка получения ссылки для загрузки."

    # args может быть пустым — защищаемся от IndexError
    first_arg = exception.args[0] if exception.args else ""
    if isinstance(first_arg, str) and (
            "Указанного пути" in first_arg or "Не авторизован" in first_arg
    ):
        return first_arg
    return f"Неизвестная ошибка ({type(exception).__name__})"


class UnauthorizedError(Exception):
    pass
