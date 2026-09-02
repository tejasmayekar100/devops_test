from conftest import login, auth_headers
import requests

PASSWORD = "pass123"


def test_employee_cannot_access_admin_only_route():
    employee_token = login(
        "employee@test.com",
        PASSWORD
    )

    response = requests.get(
        "http://127.0.0.1:3000/api/users",
        headers=auth_headers(employee_token),
    )

    assert response.status_code == 403
