import logging
import os
from fastapi import HTTPException, Response
import requests
import uuid
import base64
from api.utils.aws import get_secret
# ENV_SECRET_ARN = os.getenv("ENV_SECRET_ARN")
ENV_SECRET_ARN = "arn:aws:secretsmanager:eu-west-1:435772683141:secret:orchestrator-ai-api-env-qiCMIU"

logger = logging.getLogger(__name__)


class Model1Api:

    def __init__(self):
        # self.secret = get_secret(ENV_SECRET_ARN)
        self.host_repository = "" # self.secret["HOST_REPOSITORY"]

    def get_image_from_storage(self, image_id):
        try:
            url = f"{self.host_repository}/upscale"
            logger.info(f"[{image_id}] Model1 URL to request: {url}")

            response = requests.get(url)
            content_type = response.headers.get('Content-Type', 'application/octet-stream')
            logger.info(f"[{image_id}] Content type: {content_type}")

            return Response(content=response.content, media_type=content_type) if response.status_code == 200 else None
        
        except Exception as error:
            logger.error(f"[{image_id}] Error during Model1 Api request: {error}")
            raise HTTPException(status_code=400, detail="Error during Api request")            


    def get_image_status(self, image_id):
        try:
            url = f"{self.host_repository}/images/{image_id}/status"
            logger.info(f"[{image_id}] Model1 URL to request: {url}")
            
            response = requests.get(url)
            # logger.info(f"[{image_id}] Model1 request: {response.text}")
            return response.json() if response.status_code == 200 else None
        
        except Exception as error:
            logger.error(f"[{image_id}] Error during Model1 Api request: {error}")
            raise HTTPException(status_code=400, detail="Error during Api request")  
        

    def delete_image(self, image_id):
        try:
            url = f"{self.host_repository}/images/{image_id}"
            logger.info(f"[{image_id}] Model1 URL to request: {url}")

            response = requests.delete(url)
            logger.info(f"[{image_id}] Model1 request: {response.text}")
            return response.json() if response.status_code == 200 else None
        
        except Exception as error:
            logger.error(f"[{image_id}] Error during Model1 Api request: {error}")
            raise HTTPException(status_code=400, detail="Error during Api request")

    def update_image(self, image_metadata, image_id): # TODO: REVISAR
        try:
            url = f"{self.host_repository}/images/{image_id}"
            logger.info(f"[{image_id}] Model1 URL to request: {url}")

            headers = {"Content-Type": "application/json"}
            logger.info(f"[{image_id}] Model1 request: {image_metadata}")
            
            response = requests.put(url, headers=headers, json=image_metadata)
            logger.info(f"[{image_id}] Model1 request response: {response.text}")

            return response.json() if response.status_code == 200 else None
        
        except Exception as error:
            logger.error(f"[{image_id}] Error during Model1 Api request: {error}")
            raise HTTPException(status_code=400, detail="Error during Api request")  