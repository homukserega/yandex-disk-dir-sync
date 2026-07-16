FROM python:3.12.3-alpine

# Отключаем создание .pyc и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Создаём рабочую директорию
WORKDIR /app

# Копируем файл зависимостей (имя должно совпадать)
COPY requirements.txt ./

# Обновляем pip и устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копируем остальной код приложения (из папки src/)
COPY src/ ./

# Копируем .env (если нужен)
COPY .env ./

RUN mkdir data

CMD ["python", "main.py"]
