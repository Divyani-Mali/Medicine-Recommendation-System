from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_get_symptoms():
    response = client.get("/symptoms")
    assert response.status_code == 200
    assert "itching" in response.json()

def test_predict_valid_symptoms():
    response = client.post("/predict", json={"symptoms": ["itching", "skin_rash"]})
    assert response.status_code == 200
    data = response.json()
    assert "predicted_disease" in data
    assert data["predicted_disease"] == "Fungal infection"

def test_predict_empty_symptoms():
    response = client.post("/predict", json={"symptoms": []})
    assert response.status_code == 400

def test_history_after_prediction():
    client.post("/predict", json={"symptoms": ["itching"]})
    response = client.get("/history")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_stats_endpoint():
    response = client.get("/stats")
    assert response.status_code == 200
    assert "total_predictions" in response.json()