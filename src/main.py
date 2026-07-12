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
OVERWRITE = config["OVERWRITE"]["value"]          # перезаписывать при совпадении имён в нашем случае = true
URL_TO_UPLOAD = config["YANDEX_DISK"]["url_to_upload"]

# Шаг 1. Запрашиваем ссылку для загрузки
url = URL_TO_UPLOAD
params = {
    'path': DISK_PATH,
    'overwrite': OVERWRITE,   # можно также 'false' или не указывать
    # 'fields': 'href,method' # опционально – какие поля включить в ответ
}
headers = {
    'Authorization': f'OAuth {TOKEN}'
}

# Шаг 1. API генерирует ссылку для загрузки (для этого подставляем параметры пользователя и url)
response = requests.get(url, params=params, headers=headers)
response.raise_for_status()  # выбросит исключение при ошибке HTTP

# Шаг 2. Получаем ответ от API(ссылку для загрузки на YANDEX DISK - "href")
data = response.json()
upload_url = data['href']    # ссылка для PUT-запроса

# Шаг 3. Загружаем файл по полученной ссылке
with open(LOCAL_FILE, 'rb') as f:
    upload_response = requests.put(upload_url, data=f)
    upload_response.raise_for_status()

print('Файл успешно загружен!')
