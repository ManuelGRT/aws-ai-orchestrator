from datetime import datetime
import logging
import time
from typing import List, Optional
from uuid import uuid4
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Request, UploadFile
from pydantic import Field
from starlette_context import context, header_keys

from api.routers.logging import LoggingManager
from api.schemas import image
from api.schemas.persistance import OrchestratorApiPersistance
from api.utils import commons as utils_commons
from api.utils.dynamodb import DynamoDB
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from PIL import Image
from realesrgan_ncnn_py import Realesrgan
import io


router = APIRouter()

logger = logging.getLogger(__name__)


#################
# IMAGE UPSCALING
#################
@router.post("/upscale-image",
             responses=utils_commons.RESPONSES,
             response_model=image.UploadImageOutput,
             name="Upscale Image")
async def upscale(request: Request, file: UploadFile = File(...), image_id: Optional[str] = None):
    init_time = time.time()
    image_id_2 = str(uuid4())
    logger.info(f"Received image with ID: {image_id}")

    try:
        data = await file.read()
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Archivo no válido o no es una imagen")

    try:
        realesrgan = request.app.state.realesrgan
        up = realesrgan.process_pil(img)

        buf = io.BytesIO()
        up.save(buf, format="PNG")
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=upscaled.png"}
        )
    
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error during upscaling: {e}")
        response_time = time.time() - init_time
        raise HTTPException(
            status_code=500,
            detail="Error durante el procesado de la imagen",
            headers={"response_time": str(response_time), "image_id": image_id}
        )