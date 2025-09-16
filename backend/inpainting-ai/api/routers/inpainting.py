from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Request, UploadFile
from api.utils import commons as utils_commons
import logging
from api.routers.logging import LoggingManager

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from starlette_context import context, header_keys

from api.services import inpainting_service
from api.schemas.persistance import InpantingApiPersistance
import io
import cv2
import numpy as np
from PIL import Image
import torch

from api.utils.dynamodb import DynamoDB
from datetime import datetime
import time


router = APIRouter()

logger = logging.getLogger(__name__)

##################
# IMAGE INPAINTING
##################
@router.post("/analyze-image",
             responses=utils_commons.RESPONSES,
             name="Inpaint Image")
async def inpaint_image(
                background_tasks: BackgroundTasks,
                request: Request,
                image_id: str = Form(..., description='Part of the vehicles', example='ai service name'), 
                image_file: UploadFile = File(..., description='Image file')):
    
    logger = LoggingManager(context.get(header_keys.HeaderKeys.request_id),image_id)
    try:
        logger.info(f"Starting inpainting process...")
        init_time = time.time()
        response = await inpainting_service.inpaint_image(image_file=image_file, logger=logger)
        logger.info(f"Finishing inpainting process...")
        
        response_time = time.time() - init_time
        logger.info(f"Ai orchestrator image process time: {response_time}")

        dynamodb = DynamoDB()
        background_tasks.add_task(
            dynamodb.upload_api_persistance,
            logger=logger,
            data_api=InpantingApiPersistance(
                request_id=context.get(header_keys.HeaderKeys.request_id),
                api_id="inpainting_ai_api",
                image_id=str(image_id),
                response_latency=int(response_time*1000),
                request_datetime=datetime.utcnow().isoformat(),
                http_method=request.method,
                resource_path=str(request.url.path),
                status="200",
                error_message=None
            )
        )

        return response
        
    except (HTTPException, Exception) as error:
        logger.error(f"Error during Ai orchestrator image: {error}")
        response_time = time.time() - init_time
        status_code = getattr(error, "status_code", 400)
        detail = getattr(error, "detail", "Error during Ai orchestrator image")

        raise HTTPException(
            status_code=status_code,
            detail=detail,
            headers={"response_time": response_time,
                     "image_id": str(image_id)}
        )

    