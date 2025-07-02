from fastapi.testclient import TestClient
from server import app  # или from main import app

client = TestClient(app)

def test_login_success():
    response = client.post("/login", json={"username": "maxim", "password": "1234567890"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure():
    response = client.post("/login", json={"username": "maxim", "password": "неправильный"})
    assert response.status_code == 401