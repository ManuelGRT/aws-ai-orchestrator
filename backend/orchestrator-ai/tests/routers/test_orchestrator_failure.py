import io
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from PIL import Image

from api.routers import orchestrator


# ---- Configuración app de test ----
app = FastAPI()
app.include_router(orchestrator.router)
client = TestClient(app)


@pytest.fixture
def dummy_image():
    """Devuelve un buffer PNG válido en memoria."""
    img = Image.new("RGB", (32, 32), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_image_ai_analysis_failure(dummy_image, monkeypatch):
    monkeypatch.setattr("api.routers.orchestrator.DynamoDB", lambda: None)
    monkeypatch.setattr("api.routers.orchestrator.context.get", lambda *a, **k: "test-request-id")

    async def fake_orchestrator_process(*a, **k):
        raise HTTPException(status_code=500, detail="Mocked orchestrator error")

    monkeypatch.setattr("api.utils.orchestrator_service.orchestrator_process", fake_orchestrator_process)

    response = client.post(
        "/image-ai-analysis",
        data={"service_name": "denoising"},
        files={"image_file": ("test.png", dummy_image, "image/png")}
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Mocked orchestrator error"
    assert "image_id" in response.headers
    assert "response_time" in response.headers


'''
def test_image_ai_analysis_failure(dummy_image, monkeypatch):
    """Caso de fallo: el servicio orquestador lanza excepción."""

    monkeypatch.setattr("api.routers.orchestrator.DynamoDB", lambda: None)

    async def fake_orchestrator_process(*a, **k):
        raise HTTPException(status_code=500, detail="Mocked orchestrator error")

    monkeypatch.setattr("api.utils.orchestrator_service.orchestrator_process", fake_orchestrator_process)

    response = client.post(
        "/image-ai-analysis",
        data={"service_name": "denoising"},
        files={"image_file": ("test.png", dummy_image, "image/png")}
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Mocked orchestrator error"
    assert "image_id" in response.headers
    assert "response_time" in response.headers


def test_image_ai_analysis_failure(dummy_image, monkeypatch):
    monkeypatch.setattr("api.routers.orchestrator.DynamoDB", lambda: None)
    monkeypatch.setattr("api.routers.orchestrator.context.get", lambda *a, **k: "test-request-id")

    async def fake_orchestrator_process(*a, **k):
        raise HTTPException(status_code=500, detail="Mocked orchestrator error")

    monkeypatch.setattr("api.utils.orchestrator_service.orchestrator_process", fake_orchestrator_process)

    response = client.post(
        "/image-ai-analysis",
        data={"service_name": "denoising"},
        files={"image_file": ("test.png", dummy_image, "image/png")}
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Mocked orchestrator error"
    assert "image_id" in response.headers
    assert "response_time" in response.headers
'''

def test_get_image_failure(monkeypatch):
    """Caso de fallo: el servicio de get_image lanza excepción"""

    # Mock DynamoDB con método válido para no romper en background_tasks
    class DummyDynamo:
        def upload_api_persistance(self, *a, **k):
            return None

    monkeypatch.setattr("api.routers.orchestrator.DynamoDB", lambda: DummyDynamo())
    # Mock context.get
    monkeypatch.setattr("api.routers.orchestrator.context.get", lambda *a, **k: "test-request-id")

    # Mock service para que falle
    async def fake_get_image_process(image_id, service_name, logger):
        raise HTTPException(status_code=500, detail="Mocked get_image failure")

    monkeypatch.setattr(
        "api.utils.orchestrator_service.get_image_process",
        fake_get_image_process
    )

    response = client.get("/images/denoising/12345")

    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "Mocked get_image failure"
    assert "response_time" in response.headers
    assert response.headers["image_id"] == "12345"