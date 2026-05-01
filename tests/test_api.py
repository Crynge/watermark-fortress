from fastapi.testclient import TestClient

from apps.api.app.main import app


client = TestClient(app)


def test_overview_endpoint() -> None:
    response = client.get("/api/overview")
    assert response.status_code == 200
    payload = response.json()
    assert payload["repo_name"] == "watermark-fortress"
    assert payload["benchmark_summary"]["sample_count"] >= 1


def test_battle_endpoint() -> None:
    response = client.post(
        "/api/battle",
        json={
            "text": "Because important systems must remain robust, however, their provenance should stay visible.",
            "attack": "mixed_pressure",
        },
    )
    assert response.status_code == 200
    payload = response.json()["battle"]
    assert payload["detection_healed"]["confidence"] >= payload["detection_after"]["confidence"]
