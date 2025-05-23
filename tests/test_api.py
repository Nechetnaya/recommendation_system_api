import requests
from datetime import datetime
import time
import pytest

"""
Check 3 valid user_ids and 1 invalid
Incase invalid id, top-5 posts are returned
"""

url = "http://127.0.0.1:8000/post/recommendations/"

@pytest.mark.parametrize("user_id", [100001, 225, 1177, 0])
def test_api(user_id):
    time_str = datetime(2021, 12, 10).isoformat()
    params = {
        "user_id": user_id,
        "time": time_str,
        "limit": 5
    }

    start_time = time.time()
    response = requests.get(url, params=params)
    duration = time.time() - start_time

    assert response.status_code == 200, f"Status code: {response.status_code}"
    assert isinstance(response.json(), list), "Response is not a list"
    assert len(response.json()) == 5, f"Expected 5 posts, got {len(response.json())}"
    assert duration < 3, f"Response too slow: {duration:.2f} seconds"
