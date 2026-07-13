import requests
import configparser
import os
from dotenv import load_dotenv

load_dotenv()


# Данные для авторизации и настройки
TOKEN = os.getenv('TOKEN')
URL_TO_UPLOAD = "https://cloud-api.yandex.net/v1/disk/resources/upload"
DISK_PATH = os.getenv('DISK_PATH')
DISK_PATH = f'{DISK_PATH}/test_file_to_send.txt'    # куда сохранить на Диске

# Шаг 1. Запрашиваем ссылку для загрузки
url = URL_TO_UPLOAD
params = {
    'path': DISK_PATH,
    'overwrite': "true",   # можно также 'false' или не указывать
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
with open("test_file_to_send.txt", 'rb') as f:
    upload_response = requests.put(upload_url, data=f)
    upload_response.raise_for_status()

print('Файл успешно загружен!')
