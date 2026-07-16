FROM python:3.12-alpine

# Отключаем создание .pyc и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Создаём рабочую директорию
WORKDIR /app

# Копируем файл зависимостей (имя должно совпадать)
COPY requirements.txt ./

# Создаём виртуальное окружение и устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt


# Копируем остальной код приложения (из папки src/)
COPY src/ ./

# Копируем .env (если нужен)
COPY .env ./

# Запускаем приложение через интерпретатор виртуального окружения
# Предположим, что главный файл называется main.py
CMD ["python", "main.py"]
