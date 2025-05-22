import requests
from datetime import datetime
import time


url = "http://127.0.0.1:8000/post/recommendations/"

for user_id in range(110000, 110002):
    time_str = datetime(2021, 12, 10).isoformat()

    params = {
        "id": user_id,
        "time": time_str,
        "limit": 5
    }

    start_time = time.time()
    response = requests.get(url, params=params)
    duration = time.time() - start_time

    if response.status_code == 200:
        recommendations = response.json()
        print(f"ID: {user_id} | Время ответа: {duration:.3f} сек")
        print(f"Рекомендации: {recommendations}\n")
    else:
        print(f"ID: {user_id} | Ошибка: {response.status_code} | {response.text}\n")
