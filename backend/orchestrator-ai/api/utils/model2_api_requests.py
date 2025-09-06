import os
from fastapi import HTTPException
import requests
from api.utils.aws import get_secret
import logging

# ENV_SECRET_ARN = os.getenv("ENV_SECRET_ARN")
ENV_SECRET_ARN = "arn:aws:secretsmanager:eu-west-1:435772683141:secret:orchestrator-ai-api-env-qiCMIU"

logger = logging.getLogger(__name__)

class Model2Api:

    def __init__(self):
        # self.secret = get_secret(ENV_SECRET_ARN)
        self.host_model2 = "" # self.secret["HOST_MODEL2"]

    def deblurring(self, image):
        try:
            url = f"{self.host_model2}/deblurring"
            logger.info(f"Model URL to request: {url}")

            headers = {"Content-Type": "application/json"}
            data = {"image_type": "jpeg"}
            logger.info(f"Model request: {data}")
            
            response = requests.post(url, headers=headers, json=data)
            logger.info(f"Model request response: {response.text}")

            return response.json() if response.status_code == 200 else None
        
        except Exception as error:
            logger.error(f"Error during Model Api request: {error}")
            raise HTTPException(status_code=400, detail="Error during Api request")  
