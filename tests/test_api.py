from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_solve_square_of_sum_api():
    response = client.post(
        "/api/v1/math/solve",
        json={"expression": "(x+5)^2"},
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["topic"] == "Produtos notáveis"
    assert payload["rule_name"] == "Quadrado da soma"
    assert payload["result"] == "x^2 + 10x + 25"
    assert payload["development_line"] == (
        "(x+5)^2 = x^2 + 2 · x · 5 + 5^2 = x^2 + 10x + 25"
    )


def test_solve_unsupported_expression_api():
    response = client.post(
        "/api/v1/math/solve",
        json={"expression": "(x+5)^4"},
    )

    assert response.status_code == 400
    assert "Unsupported expression" in response.json()["detail"]