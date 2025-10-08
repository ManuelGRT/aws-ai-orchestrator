import io
import pytest
from fastapi import FastAPI
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
    img = Image.new("RGB", (32, 32), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_image_ai_analysis_success(dummy_image, monkeypatch):
    """Caso feliz: el endpoint orquesta correctamente y devuelve 200"""

    # Mock DynamoDB con método válido
    class DummyDynamo:
        def upload_api_persistance(self, *a, **k):
            return None

    monkeypatch.setattr("api.routers.orchestrator.DynamoDB", lambda: DummyDynamo())
    # Mock context.get para evitar ContextDoesNotExistError
    monkeypatch.setattr("api.routers.orchestrator.context.get", lambda *a, **k: "test-request-id")

    # Mock orchestrator_service
    async def fake_orchestrator_process(image_file, image_id, service_name, logger, background_tasks):
        return {"success": True}

    monkeypatch.setattr(
        "api.utils.orchestrator_service.orchestrator_process",
        fake_orchestrator_process
    )

    response = client.post(
        "/image-ai-analysis",
        data={"service_name": "denoising"},
        files={"image_file": ("test.png", dummy_image, "image/png")}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "image_id" in body
    assert body["message"] == "Image send to analyze successfully"


def test_get_image_success(monkeypatch):
    """Caso feliz: devuelve imagen desde S3."""

    # Mock DynamoDB con método válido
    class DummyDynamo:
        def upload_api_persistance(self, *a, **k):
            return None

    monkeypatch.setattr("api.routers.orchestrator.DynamoDB", lambda: DummyDynamo())
    # Mock context.get para evitar ContextDoesNotExistError
    monkeypatch.setattr("api.routers.orchestrator.context.get", lambda *a, **k: "test-request-id")

    async def fake_get_image_process(image_id, service_name, logger):
        from fastapi import Response
        return Response(content=b"fakeimagebytes", media_type="image/png")

    monkeypatch.setattr("api.utils.orchestrator_service.get_image_process", fake_get_image_process)

    response = client.get("/images/denoising/12345")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content == b"fakeimagebytes"