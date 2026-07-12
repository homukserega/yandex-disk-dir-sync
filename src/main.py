import requests

# Данные для авторизации и настройки
TOKEN = 'ваш_токен_доступа'            # OAuth-токен
LOCAL_FILE = 'test_file_to_send.txt'      # путь к файлу на компьютере
DISK_PATH = f'test_file_to_send/{LOCAL_FILE}'  # куда сохранить на Диске
OVERWRITE = 'true'                     # перезаписывать при совпадении имён

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