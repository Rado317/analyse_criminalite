from fastapi.testclient import TestClient

from api.main import app


def test_health_and_quality_endpoints():
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        quality = client.get("/api/v1/data-quality")
        assert quality.status_code == 200
        assert quality.json()["nombre_lignes"] > 0

        summary = client.get("/api/v1/summary")
        assert summary.status_code == 200
        assert summary.json()["lignes"] > 0
