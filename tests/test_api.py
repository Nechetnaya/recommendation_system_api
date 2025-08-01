"""
API recommendation endpoint tests.

This module tests the `/post/recommendations/` endpoint using valid and invalid user IDs.
It verifies the structure and content of the response, including the recommendations,
experiment group, and response speed.

Test cases:
- Valid user IDs should return 5 recommended posts and a valid exp_group.
- Invalid user IDs should fall back to returning top-5 posts.
"""

import requests
from datetime import datetime
import time
import pytest


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

    # Check HTTP status
    assert response.status_code == 200, f"Status code: {response.status_code}"
    # Check response type
    assert isinstance(json_response, dict), "Response is not a dict"

    # Check recommendations field exists and is a list
    assert "recommendations" in json_response, "'recommendations' not in response"
    assert isinstance(recommendations, list), "'recommendations' is not a list"
    assert len(recommendations) == 5, f"Expected 5 posts, got {len(recommendations)}"

    # Check exp_group field exists and has a valid value
    assert "exp_group" in json_response, "'exp_group' not in response"
    assert exp_group in {"control", "test"}, f"Unexpected exp_group value: {exp_group}"

    # Check response time
    assert duration < 3, f"Response too slow: {duration:.2f} seconds"
