import io
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from PIL import Image
from api.routers import denoising
from starlette_context.middleware import RawContextMiddleware


# Crear app de test con middleware de contexto
app = FastAPI()
app.add_middleware(RawContextMiddleware)
app.include_router(denoising.router)
client = TestClient(app)


@pytest.fixture
def dummy_image():
    """Genera una imagen RGB en memoria"""
    img = Image.new("RGB", (32, 32), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_denoise_endpoint_failure(dummy_image, monkeypatch):
    # Mock DynamoDB (para que no ejecute nada real)
    class DummyDynamo:
        def upload_api_persistance(self, **kwargs):
            return None

    monkeypatch.setattr("api.routers.denoising.DynamoDB", lambda: DummyDynamo())

    # Mock denoising_service para que lance un error
    def fake_denoise_image(*args, **kwargs):
        raise HTTPException(status_code=500, detail="Mocked denoising failure")

    monkeypatch.setattr("api.routers.denoising.denoising_service.denoise_image", fake_denoise_image)

    response = client.post(
        "/analyze-image",
        data={"image_id": "test_failure"},
        files={"image_file": ("test.png", dummy_image, "image/png")},
        headers={"X-Request-ID": "test-request-id"},  # inyecta contexto
    )

    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "Mocked denoising failure"
