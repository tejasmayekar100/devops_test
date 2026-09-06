from conftest import login, auth_headers

import requests


def test_expense_claim_over_policy_limit_is_rejected():
    employee_token = login(
        "employee@test.com",
        "pass123"
    )

    response = requests.post(
        "http://127.0.0.1:3000/api/expense-claims",
        headers=auth_headers(employee_token),
        json={
            "travel_request_id": 1,
            "items": [
                {
                    "category_id": 1,
                    "description": "Way too expensive hotel",
                    "amount": 999999,
                    "expense_date": "2026-09-01",
                }
            ],
        },
    )

    assert response.status_code == 400

    assert "exceeds" in response.json()["message"].lower()
