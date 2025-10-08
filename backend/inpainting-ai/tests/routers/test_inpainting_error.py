import io
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from PIL import Image
from api.routers import inpainting


# Montar la app de prueba
app = FastAPI()
app.include_router(inpainting.router)
client = TestClient(app)


@pytest.fixture
def dummy_image():
    """Imagen PNG pequeña en memoria."""
    img = Image.new("RGB", (16, 16), color="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_inpainting_endpoint_failure(dummy_image, monkeypatch):
    """Simula fallo en el servicio de inpainting."""

    # Mock DynamoDB para que no llame a AWS
    monkeypatch.setattr("api.routers.inpainting.DynamoDB", lambda: None)

    # Mock context.get para que no falle starlette_context
    monkeypatch.setattr(
        "api.routers.inpainting.context.get", lambda *a, **k: "test-request-id"
    )

    # Mock servicio de inpainting para que siempre falle
    async def fake_inpaint_image(image_file, logger):
        raise HTTPException(status_code=500, detail="Mocked inpainting error")

    monkeypatch.setattr(
        "api.routers.inpainting.inpainting_service.inpaint_image",
        fake_inpaint_image,
    )

    response = client.post(
        "/analyze-image",
        data={"image_id": "fail_test"},
        files={"image_file": ("test.png", dummy_image, "image/png")},
    )

    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "Mocked inpainting error"
    assert "response_time" in response.headers
    assert response.headers["image_id"] == "fail_test"
