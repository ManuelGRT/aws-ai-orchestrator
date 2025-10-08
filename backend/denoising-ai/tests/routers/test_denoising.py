import io
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image
from api.routers import denoising  # tu router con @router.post("/analyze-image")
from starlette_context.middleware import RawContextMiddleware

# Crear app de test con el middleware de contexto
app = FastAPI()
app.add_middleware(RawContextMiddleware)
app.include_router(denoising.router)

client = TestClient(app)


@pytest.fixture
def dummy_image():
    """Genera una imagen RGB en memoria"""
    img = Image.new("RGB", (64, 64), color="gray")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_denoise_endpoint_success(dummy_image, monkeypatch):
    """Caso exitoso de denoising"""

    # Mock DynamoDB para evitar llamadas reales
    class DummyDynamo:
        def upload_api_persistance(self, **kwargs):
            return None

    monkeypatch.setattr("api.routers.denoising.DynamoDB", lambda: DummyDynamo())

    response = client.post(
        "/analyze-image",
        data={"image_id": "test_img"},
        files={"image_file": ("test.png", dummy_image, "image/png")},
        headers={"X-Request-ID": "test-request-id"},  # inyecta el contexto
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content is not None


'''
def test_denoise_endpoint_invalid_file(monkeypatch):
    """Caso de fallo cuando el archivo no es válido"""

    class DummyDynamo:
        def upload_api_persistance(self, **kwargs):
            return None

    monkeypatch.setattr("api.routers.denoising.DynamoDB", lambda: DummyDynamo())

    fake_file = io.BytesIO(b"not-an-image")

    response = client.post(
        "/analyze-image",
        data={"image_id": "bad_img"},
        files={"image_file": ("bad.txt", fake_file, "text/plain")},
        headers={"X-Request-ID": "test-request-id"},  # inyecta el contexto
    )

    assert response.status_code == 400
    assert "Archivo no válido" in response.json()["detail"]
'''