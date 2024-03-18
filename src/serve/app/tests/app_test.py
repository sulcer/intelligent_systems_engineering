from fastapi.testclient import TestClient
from src.serve.app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_predict_multiple():
    response = client.get("/mbajk/predict/")
    assert response.status_code == 200
