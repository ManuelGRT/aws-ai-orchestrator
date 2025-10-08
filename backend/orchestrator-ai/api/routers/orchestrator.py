from datetime import datetime
import logging
import time
from uuid import uuid4
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Request, UploadFile
from pydantic import Field
from starlette_context import context, header_keys

from api.routers.logging import LoggingManager
from api.schemas import orchestrator
from api.schemas.persistance import OrchestratorApiPersistance
from api.utils import orchestrator_service
from api.utils import commons as utils_commons
from api.utils.dynamodb import DynamoDB


router = APIRouter()

# logger = logging.getLogger(__name__)


####################
# IMAGE ORCHESTRATOR
####################
@router.post("/image-ai-analysis",
             responses=utils_commons.RESPONSES,
             response_model=orchestrator.UploadImageOutput,
             name="Upload Image")
async def image_ai_analysis(
                 background_tasks: BackgroundTasks,
                 request: Request,       
                 service_name: str = Form(..., description='Part of the vehicles', example='ai service name'), 
                 image_file: UploadFile = File(..., description='Image file')):
    '''
    Upload image
    :body service_name
    :body image_file: Image
    '''
    image_id = str(uuid4())
    logger = LoggingManager(context.get(header_keys.HeaderKeys.request_id),image_id)
    logger.info(f"SERVICE NAME: {service_name}")
    try:
        logger.info(f"Starting ai orchestrator process...")
        init_time = time.time()
        orchestrator_result = await orchestrator_service.orchestrator_process(
            image_file=image_file,
            image_id=image_id,
            service_name=service_name,
            logger=logger,
            background_tasks=background_tasks
        ) 
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
            "success": orchestrator_result["success"],
            "message": f"Image send to analyze successfully",
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
            headers={"response_time": str(response_time),
                     "image_id": str(image_id)}
        )
    

###########
# GET IMAGE
###########
@router.get("/images/{service_name}/{image_id}",
            responses=utils_commons.RESPONSES,
            name="Get Image")
async def get_image(
                background_tasks: BackgroundTasks,
                image_id: str,
                service_name: str,
                request: Request):
    
    '''
    Get image
    :param image_id: Image id
    :body service_name
    :return: Image file
    '''

    logger = LoggingManager(context.get(header_keys.HeaderKeys.request_id),image_id)

    try:
        logger.info(f"Starting get image process...")
        init_time = time.time()
 
        image_result = await orchestrator_service.get_image_process(
            image_id=image_id,
            service_name=service_name,
            logger=logger
        )
        
        logger.info(f"Finishing get image process...")
        response_time = time.time() - init_time
        logger.info(f"Get image process time: {response_time}")

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

        return image_result
    
    except (HTTPException, Exception) as error:
        logger.error(f"Error during get image: {error}")
        response_time = time.time() - init_time
        status_code = getattr(error, "status_code", 400)
        detail = getattr(error, "detail", "Error during get image")

        raise HTTPException(
            status_code=status_code,
            detail=detail,
            headers={"response_time": str(response_time),
                     "image_id": str(image_id)}
        )