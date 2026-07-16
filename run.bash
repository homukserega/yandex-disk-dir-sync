#!/usr/bin/bash
# Скрипт для запуска docker-compose с запросом пути монтирования

echo "Введите абсолютный путь к синхронизируемому каталогу."
echo "Пример: /home/user/Downloads."
read -r HOST_PATH

# Проверяем, существует ли каталог
if [ ! -d "$HOST_PATH" ]; then
    echo "Ошибка: каталог '$HOST_PATH' не существует."
    exit 1
fi

# Экспортируем переменную для docker-compose
export HOST_PATH

# Запускаем контейнеры
docker compose up
