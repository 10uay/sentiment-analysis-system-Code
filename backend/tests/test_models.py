from app.services.model_orchestrator import ModelOrchestrator


def test_model_prediction():
    orch = ModelOrchestrator()
    results = orch.predict("I love this excellent product", language="en", model_name="ensemble")
    assert len(results) >= 1
    final = orch.aggregate(results)
    assert final["label"] in ["positive", "negative", "neutral", "very_positive", "very_negative"]
