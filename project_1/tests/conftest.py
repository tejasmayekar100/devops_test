import requests

BASE_URL = "http://127.0.0.1:3000"
PASSWORD = "pass123"


def login(email, password):
    response = requests.post(
        f"{BASE_URL}/api/login",
        json={
            "email": email,
            "password": password,
        }
    )

    assert response.status_code == 200, (
        f"Login failed for {email}: {response.text}"
    )

    return response.json()["access_token"]


def auth_headers(token):
    return {
        "Authorization": f"Bearer {token}"
    }
