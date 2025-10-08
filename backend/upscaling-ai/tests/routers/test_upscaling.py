import io
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from PIL import Image
from api.routers import upscaling


# Montamos la app de prueba
app = FastAPI()

# Inyectamos un "fake realesrgan" en app.state
class DummyRealesrgan:
    def process_pil(self, img):
        return img  # simplemente devuelve la misma imagen

app.state.realesrgan = DummyRealesrgan()
app.include_router(upscaling.router)

client = TestClient(app)


@pytest.fixture
def dummy_image():
    """Genera una imagen pequeña RGB en memoria."""
    img = Image.new("RGB", (16, 16), color="green")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_upscaling_success(dummy_image, monkeypatch):
    """Caso feliz: el endpoint devuelve una imagen PNG."""
    # Mock DynamoDB → ahora devuelve un objeto con el método upload_api_persistance
    class DummyDynamo:
        def upload_api_persistance(self, *a, **k):
            return None

    monkeypatch.setattr("api.routers.upscaling.DynamoDB", lambda: DummyDynamo())

    # Mock context.get
    monkeypatch.setattr("api.routers.upscaling.context.get", lambda *a, **k: "test-request-id")

    response = client.post(
        "/analyze-image",
        data={"image_id": "upscale_test"},
        files={"image_file": ("test.png", dummy_image, "image/png")},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.headers["Content-Disposition"] == "inline; filename=upscaled.png"
    assert response.content  # hay bytes de imagen


def test_upscaling_failure(dummy_image, monkeypatch):
    """Caso de fallo: el servicio de upscaling lanza excepción."""

    # Mock DynamoDB
    class DummyDynamo:
        def upload_api_persistance(self, *a, **k):
            return None

    monkeypatch.setattr("api.routers.upscaling.DynamoDB", lambda: DummyDynamo())

    # Mock context.get
    monkeypatch.setattr("api.routers.upscaling.context.get", lambda *a, **k: "test-request-id")

    # Mock servicio de upscaling para forzar un error
    async def fake_upscale_image(image_file, logger, request):
        raise HTTPException(status_code=500, detail="Mocked upscaling failure")

    monkeypatch.setattr("api.routers.upscaling.upscaling_service.upscale_image", fake_upscale_image)

    response = client.post(
        "/analyze-image",
        data={"image_id": "fail_upscale"},
        files={"image_file": ("test.png", dummy_image, "image/png")},
    )

    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "Mocked upscaling failure"
    assert "response_time" in response.headers
    assert response.headers["image_id"] == "fail_upscale"