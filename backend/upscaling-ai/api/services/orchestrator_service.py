from io import BytesIO
from api.routers.logging import LoggingManager
from api.schemas import image
from api.utils.s3_bucket import S3Bucket
from sqlmodel import Session, select
from fastapi import BackgroundTasks, HTTPException, Request, UploadFile
import base64
from api.utils import commons as utils_commons

from datetime import datetime
from uuid import uuid4
import time

async def save_new_image(image_file: UploadFile, image_id: str, logger: LoggingManager):
    try:
        file_content = await image_file.read()
        file = BytesIO(file_content)
        logger.info(f"Begin image upload to S3 bucket...")
        s3Bucket = S3Bucket()
        s3Bucket.upload_image(logger=logger, 
                              image=file, 
                              image_id=image_id, 
                              image_prefix="images/", 
                              content_type=image_file.content_type)
        logger.info(f"Ending image upload to S3 bucket...")
        
        return {'success' : True}

    except Exception as error:
        logger.error(f"Error during create image: {error}")
        raise HTTPException(status_code=400, detail=f"Error during create image")