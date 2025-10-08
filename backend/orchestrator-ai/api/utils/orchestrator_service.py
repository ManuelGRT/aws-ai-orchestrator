from io import BytesIO
import io

from fastapi.concurrency import run_in_threadpool
from api.routers.logging import LoggingManager
from api.utils.s3_bucket import S3Bucket
from fastapi import BackgroundTasks, HTTPException, Response, UploadFile
from api.utils.modelai_api_requests import ModelAiApi


async def save_new_image(image_bytes: bytes, 
                        image_id: str, 
                        image_prefix: str, 
                        logger: LoggingManager, 
                        content_type: str = "image/png"):
    """
    Guarda imagen desde bytes directamente
    """
    try:
        logger.info(f"Begin image upload to S3 bucket...")
        file = BytesIO(image_bytes)
        s3Bucket = S3Bucket()
        s3Bucket.upload_image(logger=logger, 
                              image=file, 
                              image_id=image_id, 
                              image_prefix=image_prefix, 
                              content_type=content_type)
        logger.info(f"Ending image upload to S3 bucket...")
        
        return {'success': True}

    except Exception as error:
        logger.error(f"Error during create image: {error}")
        raise HTTPException(status_code=400, detail=f"Error during create image")


async def analyze_new_image(image_bytes: bytes, image_id: str, service_name: str, logger: LoggingManager):
    """
    Analiza la imagen y guarda el resultado
    """
    try:
        logger.info(f"Analyzing image with AI service {service_name}...")
        
        # Llamar a la API de análisis en un thread pool para no bloquear
        upscale_api = ModelAiApi()
        response_image_bytes = await run_in_threadpool(
            lambda: upscale_api.analyze_image(
                image_bytes=image_bytes,
                image_id=image_id,
                service_name=service_name,
                logger=logger
            )
        )

        if response_image_bytes is None:
            raise HTTPException(status_code=400, detail="Error Getting Api Info")
        
        logger.info(f"Image analyzed successfully.")

        # Guardar la imagen procesada
        await save_new_image(
            image_bytes=response_image_bytes,
            image_id=image_id,
            image_prefix=service_name,
            logger=logger,
            content_type="image/png"
        )
    
    except Exception as error:
        logger.error(f"Error during analyze image: {error}")
        raise HTTPException(status_code=400, detail=f"Error during analyze image")
    

async def orchestrator_process(image_file: UploadFile, image_id: str, service_name: str, logger: LoggingManager, background_tasks: BackgroundTasks):
    """
    Orquesta el proceso completo: guarda la imagen original y programa el análisis
    """
    try:
        logger.info(f"Starting orchestrator process for image {image_id}")
        
        # Leer los bytes UNA SOLA VEZ
        image_bytes = await image_file.read()
        
        # Guardar imagen original
        logger.info(f"Saving original image...")
        await save_new_image(
            image_bytes=image_bytes,
            image_id=image_id,
            image_prefix="input",
            logger=logger,
            content_type=image_file.content_type
        )
        logger.info(f"Original image saved successfully.")

        background_tasks.add_task(
            analyze_new_image,
            image_bytes=image_bytes,
            image_id=image_id,
            service_name=service_name,
            logger=logger
        )
        
        return {'success': True}
    
    except Exception as error:
        logger.error(f"Error during orchestrator process: {error}")
        raise HTTPException(status_code=400, detail=f"Error during orchestrator process")
    

async def get_image_process(image_id: str, service_name: str, logger: LoggingManager):
    try:
        logger.info(f"Getting image from S3 bucket...")
        s3Bucket = S3Bucket()
        image_url = s3Bucket.presigned_url(logger=logger,
                                           image_id=image_id, 
                                           image_prefix=service_name + "-images/",
                                           extension='png')
        logger.info(f"Presigned URL: {image_url}")
        image_bytes = s3Bucket.get_image(logger=logger, image_url=image_url)
        logger.info(f"Image retrieved successfully from S3 bucket.")

        return Response(content=image_bytes.content, media_type="image/png")
    
    except Exception as error:
        logger.error(f"Error during get image: {error}")
        raise HTTPException(status_code=400, detail=f"Error during get image")