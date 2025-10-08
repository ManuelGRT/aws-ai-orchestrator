import io
import pytest
from fastapi import UploadFile, HTTPException, Response, BackgroundTasks

import api.utils.orchestrator_service as service


# ==== Fixtures ====
@pytest.fixture
def dummy_logger():
    return type("DummyLogger", (), {"info": print, "error": print})()


@pytest.fixture
def dummy_image_bytes():
    return b"fakeimagedata"


# ==== save_new_image ====
@pytest.mark.asyncio
async def test_save_new_image_success(monkeypatch, dummy_logger, dummy_image_bytes):
    """Debe llamar a S3Bucket.upload_image y devolver success=True"""

    class DummyS3:
        def upload_image(self, *a, **k): return None

    monkeypatch.setattr(service, "S3Bucket", lambda: DummyS3())

    result = await service.save_new_image(
        image_bytes=dummy_image_bytes,
        image_id="123",
        image_prefix="input",
        logger=dummy_logger
    )
    assert result == {"success": True}


@pytest.mark.asyncio
async def test_save_new_image_failure(monkeypatch, dummy_logger, dummy_image_bytes):
    """Si falla el upload_image debe lanzar HTTPException(400)"""

    class DummyS3:
        def upload_image(self, *a, **k): raise Exception("S3 failure")

    monkeypatch.setattr(service, "S3Bucket", lambda: DummyS3())

    with pytest.raises(HTTPException) as excinfo:
        await service.save_new_image(dummy_image_bytes, "123", "input", dummy_logger)

    assert excinfo.value.status_code == 400


# ==== analyze_new_image ====
@pytest.mark.asyncio
async def test_analyze_new_image_success(monkeypatch, dummy_logger, dummy_image_bytes):
    """Debe analizar la imagen y guardar el resultado en S3"""

    class DummyApi:
        def analyze_image(self, *a, **k): return b"processed_image"

    class DummyS3:
        def upload_image(self, *a, **k): return None

    monkeypatch.setattr(service, "ModelAiApi", lambda: DummyApi())
    monkeypatch.setattr(service, "S3Bucket", lambda: DummyS3())

    result = await service.analyze_new_image(dummy_image_bytes, "123", "denoise", dummy_logger)
    assert result is None


@pytest.mark.asyncio
async def test_analyze_new_image_failure(monkeypatch, dummy_logger, dummy_image_bytes):
    """Si la API devuelve None debe lanzar HTTPException"""

    class DummyApi:
        def analyze_image(self, *a, **k): return None

    monkeypatch.setattr(service, "ModelAiApi", lambda: DummyApi())

    with pytest.raises(HTTPException) as excinfo:
        await service.analyze_new_image(dummy_image_bytes, "123", "denoise", dummy_logger)

    assert excinfo.value.status_code == 400


# ==== orchestrator_process ====
@pytest.mark.asyncio
async def test_orchestrator_process_success(monkeypatch, dummy_logger, dummy_image_bytes):
    """Debe guardar la imagen original y programar analyze_new_image en background"""

    class DummyS3:
        def upload_image(self, *a, **k): return None

    monkeypatch.setattr(service, "S3Bucket", lambda: DummyS3())

    # Crear un UploadFile falso
    upload = UploadFile(filename="test.png", file=io.BytesIO(dummy_image_bytes))

    background_tasks = BackgroundTasks()
    result = await service.orchestrator_process(upload, "123", "denoise", dummy_logger, background_tasks)

    assert result == {"success": True}
    assert len(background_tasks.tasks) == 1


@pytest.mark.asyncio
async def test_orchestrator_process_failure(monkeypatch, dummy_logger):
    """Si save_new_image falla, debe lanzar HTTPException"""

    async def fake_save_new_image(*a, **k): raise Exception("boom")
    monkeypatch.setattr(service, "save_new_image", fake_save_new_image)

    upload = UploadFile(filename="test.png", file=io.BytesIO(b"badbytes"))
    background_tasks = BackgroundTasks()

    with pytest.raises(HTTPException) as excinfo:
        await service.orchestrator_process(upload, "123", "denoise", dummy_logger, background_tasks)

    assert excinfo.value.status_code == 400


# ==== get_image_process ====
@pytest.mark.asyncio
async def test_get_image_process_success(monkeypatch, dummy_logger):
    """Debe devolver un Response con la imagen recuperada"""

    class DummyResponse:
        content = b"retrieved_bytes"

    class DummyS3:
        def presigned_url(self, *a, **k): return "http://fake-url"
        def get_image(self, *a, **k): return DummyResponse()

    monkeypatch.setattr(service, "S3Bucket", lambda: DummyS3())

    response = await service.get_image_process("123", "denoise", dummy_logger)
    assert isinstance(response, Response)
    assert response.body == b"retrieved_bytes"
    assert response.media_type == "image/png"


@pytest.mark.asyncio
async def test_get_image_process_failure(monkeypatch, dummy_logger):
    """Si S3 falla debe lanzar HTTPException"""

    class DummyS3:
        def presigned_url(self, *a, **k): return "http://fake-url"
        def get_image(self, *a, **k): raise Exception("S3 fail")

    monkeypatch.setattr(service, "S3Bucket", lambda: DummyS3())

    with pytest.raises(HTTPException) as excinfo:
        await service.get_image_process("123", "denoise", dummy_logger)

    assert excinfo.value.status_code == 400
