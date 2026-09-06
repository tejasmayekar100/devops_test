import requests

BASE_URL = "http://127.0.0.1:3000"
PASSWORD = "pass123"


def test_login_with_correct_password():
    response = requests.post(
        f"{BASE_URL}/api/login",
        json={
            "email": "employee@test.com",
            "password": PASSWORD,
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["user"]["role"] == "EMPLOYEE"
