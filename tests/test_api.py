import requests
from datetime import datetime
import time
import pytest

"""
Check 3 valid user_ids and 1 invalid
Incase invalid id, top-5 posts are returned
"""

url = "http://127.0.0.1:8000/post/recommendations/"

@pytest.mark.parametrize("user_id", [100001, 225, 1177])
def test_api(user_id):
    time_str = datetime(2021, 12, 10).isoformat()
    params = {
        "user_id": user_id,
        # "id": user_id,
        "time": time_str,
        "limit": 5
    }

    start_time = time.time()
    response = requests.get(url, params=params)
    duration = time.time() - start_time

    json_response = response.json()
    recommendations = json_response["recommendations"]
    exp_group = json_response["exp_group"]

    assert response.status_code == 200, f"Status code: {response.status_code}"
    assert isinstance(json_response, dict), "Response is not a dict"

    # Проверка поля recommendations
    assert "recommendations" in json_response, "'recommendations' not in response"
    assert isinstance(recommendations, list), "'recommendations' is not a list"
    assert len(recommendations) == 5, f"Expected 5 posts, got {len(recommendations)}"

    # Проверка поля exp_group
    assert "exp_group" in json_response, "'exp_group' not in response"
    assert exp_group in {"control", "test"}, f"Unexpected exp_group value: {exp_group}"

    # Проверка скорости ответа
    assert duration < 3, f"Response too slow: {duration:.2f} seconds"
