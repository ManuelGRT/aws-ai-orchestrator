from datetime import datetime
import logging
import time
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Request, UploadFile
from pydantic import Field
from starlette_context import context, header_keys

from api.routers.logging import LoggingManager
from api.schemas.persistance import UpsaclingApiPersistance
from api.utils import commons as utils_commons
from api.utils.dynamodb import DynamoDB

from api.utils import upscaling_service

router = APIRouter()
logger = logging.getLogger(__name__)


#################
# IMAGE UPSCALING
#################
@router.post("/analyze-image",
             responses=utils_commons.RESPONSES,
             name="Upscale Image")
async def upscale(
                background_tasks: BackgroundTasks,
                request: Request,
                image_id: str = Form(..., description='Part of the vehicles', example='ai service name'), 
                image_file: UploadFile = File(..., description='Image file')):

    logger = LoggingManager(context.get(header_keys.HeaderKeys.request_id),image_id)
    try:
        logger.info(f"Starting upscaling process...")
        init_time = time.time()
        response = await upscaling_service.upscale_image(image_file=image_file, logger=logger, request=request)
        logger.info(f"Finishing upscaling process...")
        
        response_time = time.time() - init_time
        logger.info(f"Ai upscaling image process time: {response_time}")

        dynamodb = DynamoDB()
        background_tasks.add_task(
            dynamodb.upload_api_persistance,
            logger=logger,
            data_api=UpsaclingApiPersistance(
                request_id=context.get(header_keys.HeaderKeys.request_id),
                api_id="upscaling_ai_api",
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
        logger.error(f"Error during Ai upscaling image: {error}")
        response_time = time.time() - init_time
        status_code = getattr(error, "status_code", 400)
        detail = getattr(error, "detail", "Error during Ai upscaling image")

        raise HTTPException(
            status_code=status_code,
            detail=detail,
            headers={"response_time": response_time,
                     "image_id": str(image_id)}
        )