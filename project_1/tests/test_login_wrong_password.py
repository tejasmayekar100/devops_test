import requests

BASE_URL = "http://127.0.0.1:3000"


def test_login_with_wrong_password_is_rejected():
    response = requests.post(
        f"{BASE_URL}/api/login",
        json={
            "email": "employee@test.com",
            "password": "definitely_wrong_password",
        }
    )

    assert response.status_code == 401

    assert "Invalid email or password" in response.json()["message"]
