from api.routers.logging import LoggingManager

from fastapi import HTTPException, Request, UploadFile

from api.routers.logging import LoggingManager
from fastapi.responses import StreamingResponse
from PIL import Image
from realesrgan_ncnn_py import Realesrgan
import io


async def upscale_image(image_file: UploadFile, logger: LoggingManager, request: Request):
    logger.info(f"Opening image...")
    try:
        data = await image_file.read()
        img = Image.open(io.BytesIO(data)).convert("RGB")

    except Exception:
        raise HTTPException(status_code=400, detail="Archivo no válido o no es una imagen")

    logger.info("Upscaling image...")
    realesrgan = request.app.state.realesrgan
    up = realesrgan.process_pil(img)
    logger.info("Image upscaled successfully")

    logger.info("Preparing response...")
    buf = io.BytesIO()
    up.save(buf, format="PNG")
    buf.seek(0)
    logger.info("Response ready")

    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Content-Disposition": "inline; filename=upscaled.png"}
    )