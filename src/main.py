import requests
import configparser
import os
config = configparser.ConfigParser()
config_file = "../app-config.ini"
config_file_path = os.path.join("..", "app-config.ini")

# Данные для авторизации и настройки
config.read(config_file_path)
TOKEN = config["TOKEN"]["oath_token"]
LOCAL_FILE = config["LOCAL"]["file"]              # локальный файл
YANDEX_DISK_PATH = config["YANDEX_DISK"]["path"]
DISK_PATH = f'{YANDEX_DISK_PATH}/{LOCAL_FILE}'    # куда сохранить на Диске
OVERWRITE = config["OVERWRITE"]["value"]          # перезаписывать при совпадении имён

# Шаг 1. Запрашиваем ссылку для загрузки
url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
params = {
    'path': DISK_PATH,
    'overwrite': OVERWRITE,   # можно также 'false' или не указывать
    # 'fields': 'href,method' # опционально – какие поля включить в ответ
}
headers = {
    'Authorization': f'OAuth {TOKEN}'
}

response = requests.get(url, params=params, headers=headers)
response.raise_for_status()  # выбросит исключение при ошибке HTTP

data = response.json()
upload_url = data['href']    # ссылка для PUT-запроса

# Шаг 2. Загружаем файл по полученной ссылке
with open(LOCAL_FILE, 'rb') as f:
    upload_response = requests.put(upload_url, data=f)
    upload_response.raise_for_status()

print('Файл успешно загружен!')
