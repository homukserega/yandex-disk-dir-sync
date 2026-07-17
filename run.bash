#!/bin/bash
# Скрипт для запуска docker-compose с запросом пути монтирования

echo "Введите абсолютный путь к синхронизируемому каталогу."
echo "Пример: /home/user/Downloads."
read -r -p " > " HOST_PATH

# Проверяем, существует ли каталог
if [ ! -d "$HOST_PATH" ]; then
    echo "Ошибка: каталог '$HOST_PATH' не существует."
    exit 1
fi

# Экспортируем переменную для docker-compose
export HOST_PATH

# Запускаем контейнеры
echo -e "\nВведите режим запуска:"
read -r -p "Enter - обычный; d - фоновый"  COMPOSE_MODE

if [ "$COMPOSE_MODE" == "d" ]; then
    docker compose up --build -d
    echo "Для остановки и удаления сервиса запустите: './stop.bash'"
else
    docker compose up --build
    docker compose down
fi
