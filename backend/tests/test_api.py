from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze():
    response = client.post(
        "/api/v1/analyze",
        json={"text": "هذا المنتج رائع ومفيد", "model_name": "ensemble", "use_rag": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert "final_label" in data
    assert data["language"] == "ar"
