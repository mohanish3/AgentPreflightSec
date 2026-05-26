from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from agentpreflight.api.main import app, reset_rate_limits

ROOT = Path(__file__).resolve().parents[1]


def test_healthz() -> None:
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_scan_endpoint_runs_offline_path_scan() -> None:
    client = TestClient(app)

    response = client.post("/v1/scans", json={
        "target": {"type": "path", "path": str(ROOT / "demo" / "clean")},
        "profile": "strict",
        "offline": True,
    })

    assert response.status_code == 200
    payload = response.json()
    assert payload["tool"] == "AgentPreflight"
    assert payload["trust_score"] == 100
    assert payload["verdict"] == "pass"


def test_scan_endpoint_rejects_remote_mode() -> None:
    client = TestClient(app)

    response = client.post("/v1/scans", json={
        "target": {"type": "path", "path": str(ROOT / "demo" / "clean")},
        "offline": False,
    })

    assert response.status_code == 400


def test_scan_endpoint_requires_api_key_when_configured(monkeypatch) -> None:
    reset_rate_limits()
    monkeypatch.setenv("AGENTPREFLIGHT_API_KEY", "test-key")
    client = TestClient(app)

    missing = client.post("/v1/scans", json={
        "target": {"type": "path", "path": str(ROOT / "demo" / "clean")},
    })
    wrong = client.post("/v1/scans", headers={"x-agentpreflight-key": "bad"}, json={
        "target": {"type": "path", "path": str(ROOT / "demo" / "clean")},
    })
    ok = client.post("/v1/scans", headers={"x-agentpreflight-key": "test-key"}, json={
        "target": {"type": "path", "path": str(ROOT / "demo" / "clean")},
    })

    assert missing.status_code == 401
    assert wrong.status_code == 403
    assert ok.status_code == 200


def test_scan_endpoint_rate_limits(monkeypatch) -> None:
    reset_rate_limits()
    monkeypatch.delenv("AGENTPREFLIGHT_API_KEY", raising=False)
    monkeypatch.setenv("AGENTPREFLIGHT_RATE_LIMIT_PER_MINUTE", "1")
    client = TestClient(app)
    payload = {"target": {"type": "path", "path": str(ROOT / "demo" / "clean")}}

    first = client.post("/v1/scans", json=payload)
    second = client.post("/v1/scans", json=payload)

    assert first.status_code == 200
    assert second.status_code == 429
