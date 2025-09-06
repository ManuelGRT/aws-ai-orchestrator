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
from api.services import orchestrator_service, auth_service
from api.utils import commons as utils_commons
from api.utils.dynamodb import DynamoDB
from api.utils.model1_api_requests import ModelAiApi  # Make sure this import path is correct


router = APIRouter()

logger = logging.getLogger(__name__)


#################
# IMAGE ORCHESTRATOR
#################
@router.post("/image-ai-analysis",
             responses=utils_commons.RESPONSES,
             response_model=image.UploadImageOutput,
             name="Upload Image")
async def image_ai_analysis(
                 background_tasks: BackgroundTasks,
                 request: Request,       
                 service_name: str = Form(..., description='Part of the vehicles', example='ai service name'), 
                 image_file: UploadFile = File(..., description='Image files')):
    '''
    Upload image
    :param input: Input body
    :body service_name
    :body image_file: Image
    '''

    # auth_service.verify_token(request)
    image_id = str(uuid4())
    logger = LoggingManager(context.get(header_keys.HeaderKeys.request_id),image_id)
    try:
        init_time = time.time()

        logger.info(f"Starting ai orchestrator process...")
        image_result = await orchestrator_service.save_new_image(
            image_file, image_id, logger
        )

        upscale_api = ModelAiApi()
        image_file.file.seek(0)
        response_ai_api = upscale_api.analyze_image(
            image_bytes=image_file.file, image_id=image_id, service_name="upscale-image", logger=logger
        )
        if response_ai_api is None:
            raise HTTPException(status_code=400, detail="Error Getting Api Info")

        # TODO: SEND IMAGE TO MODELS FOR AI ANALYSIS
        logger.info(f"Finishing ai orchestrator process...")

        response_time = time.time() - init_time
        logger.info(f"Ai orchestrator image process time: {response_time}")

        dynamodb = DynamoDB()
        background_tasks.add_task(
            dynamodb.upload_api_persistance,
            logger=logger,
            data_api=OrchestratorApiPersistance(
                request_id=context.get(header_keys.HeaderKeys.request_id),
                api_id="orchestrator_ai_api",
                image_id=str(image_id),
                response_latency=int(response_time*1000),
                request_datetime=datetime.utcnow().isoformat(),
                http_method=request.method,
                resource_path=str(request.url.path),
                status="200",
                error_message=None
            )
        )

        return {
            "success": image_result["success"],
            "message": f"Image analyzed successfully",
            "image_id": str(image_id)
            }
        
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