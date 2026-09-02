import requests

BASE_URL = "http://127.0.0.1:3000"


def test_protected_route_without_token_is_rejected():
    response = requests.get(
        f"{BASE_URL}/api/employees"
    )

    assert response.status_code == 401
    assert response.json()["error"] == "unauthorized"
