import io
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from PIL import Image
from api.routers import inpainting
from starlette_context.middleware import RawContextMiddleware


# Crear app de test con el middleware de contexto
app = FastAPI()
app.add_middleware(RawContextMiddleware)
app.include_router(inpainting.router)

client = TestClient(app)


@pytest.fixture
def dummy_image():
    """Genera una imagen RGB en memoria"""
    img = Image.new("RGB", (64, 64), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


from fastapi.responses import StreamingResponse

def test_inpaint_endpoint_success(dummy_image, monkeypatch):
    """Caso exitoso de inpainting"""

    # Mock DynamoDB para que no toque boto3
    monkeypatch.setattr(
        "api.routers.inpainting.DynamoDB",
        lambda: type("DummyDynamo", (), {"upload_api_persistance": lambda *a, **k: None})()
    )

    # Mock del servicio de inpainting
    async def fake_inpaint_image(image_file, logger):
        buf = io.BytesIO()
        img = Image.new("RGB", (64, 64), color="green")
        img.save(buf, format="PNG")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")

    monkeypatch.setattr("api.utils.inpainting_service.inpaint_image", fake_inpaint_image)

    response = client.post(
        "/analyze-image",
        data={"image_id": "test_img"},
        files={"image_file": ("test.png", dummy_image, "image/png")},
        headers={"X-Request-ID": "test-request-id"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"  # ✅ se asegura tipo
    assert len(response.content) > 100  # ahora sí hay bytes de imagen