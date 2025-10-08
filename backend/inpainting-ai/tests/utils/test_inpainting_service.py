import io
import numpy as np
import pytest
from PIL import Image
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse

import api.utils.inpainting_service as service


def make_dummy_image(color="white", size=(32, 32)) -> Image.Image:
    """Genera una imagen pequeña para pruebas"""
    return Image.new("RGB", size, color=color)


def test_ocr_text_mask_detects_box(monkeypatch):
    """Debe devolver una máscara binaria con rectángulo cuando OCR detecta texto"""

    pil_img = make_dummy_image()

    # Mock reader.readtext para que siempre devuelva un box válido
    monkeypatch.setattr(
        service.reader,
        "readtext",
        lambda *a, **k: [([[0, 0], [10, 0], [10, 10], [0, 10]], "txt", 0.9)],
    )

    mask = service.ocr_text_mask(pil_img)
    assert mask.shape == (32, 32)
    assert mask.dtype == np.uint8
    assert mask.max() == 255


def test_ocr_text_mask_empty(monkeypatch):
    """Si OCR no detecta nada, la máscara debe estar vacía"""
    pil_img = make_dummy_image()

    monkeypatch.setattr(service.reader, "readtext", lambda *a, **k: [])
    mask = service.ocr_text_mask(pil_img)
    assert mask.sum() == 0


@pytest.mark.parametrize("dtype,max_val", [
    (np.float32, 1.0),   # float en [0,1]
    (np.float32, 255.0), # float en [0,255]
    (np.uint8, 255),     # ya uint8
])
def test_normalize_result(monkeypatch, dtype, max_val):
    """Debe devolver un array RGB uint8"""
    arr = np.ones((4, 4, 3), dtype=dtype) * max_val
    norm = service.normalize_result(arr)
    assert norm.dtype == np.uint8
    assert norm.shape == (4, 4, 3)


@pytest.mark.asyncio
async def test_inpaint_image_no_text(monkeypatch):
    """Si no hay texto detectado, devuelve la imagen original como StreamingResponse"""

    pil_img = make_dummy_image("blue")
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    buf.seek(0)
    upload = UploadFile(filename="test.png", file=io.BytesIO(buf.getvalue()))

    # Mock OCR → máscara vacía
    monkeypatch.setattr(service, "ocr_text_mask", lambda _: np.zeros((32, 32), np.uint8))

    # Mock lama para que no se llame
    monkeypatch.setattr(service, "lama", lambda *a, **k: None)

    logger = type("DummyLogger", (), {"info": print, "error": print})()

    response = await service.inpaint_image(upload, logger)
    assert isinstance(response, StreamingResponse)


@pytest.mark.asyncio
async def test_inpaint_image_with_text(monkeypatch):
    """Si hay texto, debe llamar a lama y devolver imagen procesada"""
    pil_img = make_dummy_image("red")
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    buf.seek(0)
    upload = UploadFile(filename="test.png", file=io.BytesIO(buf.getvalue()))

    # Mock OCR → máscara llena
    monkeypatch.setattr(service, "ocr_text_mask", lambda _: np.ones((32, 32), np.uint8))

    # Mock lama → devuelve numpy array RGB
    monkeypatch.setattr(service, "lama", lambda img, mask, cfg: np.zeros((32, 32, 3), dtype=np.uint8))

    logger = type("DummyLogger", (), {"info": print, "error": print})()

    response = await service.inpaint_image(upload, logger)
    assert isinstance(response, StreamingResponse)


@pytest.mark.asyncio
async def test_inpaint_image_open_error(monkeypatch):
    """Si no puede abrir la imagen, debe lanzar HTTPException(400)"""

    upload = UploadFile(filename="bad.png", file=io.BytesIO(b"not an image"))

    logger = type("DummyLogger", (), {"info": print, "error": print})()

    with pytest.raises(HTTPException) as excinfo:
        await service.inpaint_image(upload, logger)

    assert excinfo.value.status_code == 400
