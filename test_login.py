from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_salary_without_token():
    response = client.get("/salary")
    assert response.status_code == 403  # Нет заголовка Authorization

def test_salary_with_valid_token():
    login = client.post("/login", json={"username": "maxim", "password": "1234567890"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/salary", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "maxim"