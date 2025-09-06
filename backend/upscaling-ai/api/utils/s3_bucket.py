import logging
import os
import calendar
from typing import Sequence
import base64
import json
import boto3
from fastapi import HTTPException, UploadFile
import requests
from decimal import Decimal
from botocore.client import Config
from api.routers.logging import LoggingManager
# from aws_xray_sdk.core import xray_recorder

from api.utils.aws import get_secret

logger = logging.getLogger(__name__)

# ENV_SECRET_ARN = os.getenv("ENV_SECRET_ARN")
ENV_SECRET_ARN = "arn:aws:secretsmanager:eu-west-1:435772683141:secret:orchestrator-ai-api-env-qiCMIU"

REGION = os.getenv('AWS_DEFAULT_REGION')


EXTENSION = 'jpeg'

class S3Bucket():
    def __init__(self):
        # secret = get_secret(ENV_SECRET_ARN)
        self.BUCKET_NAME = "orchestrator-ai-images" #secret['BUCKET_NAME']
        # AWS Clients
        self.s3    = boto3.client('s3')
        self.s3v4 = boto3.client('s3', config=Config(signature_version='s3v4'))

    def upload_image(self, logger: LoggingManager, image, image_id: str, image_prefix: str, content_type: str="image/jpeg"):
        try:
            # content_type = image.content_type # REVISAR
            extension = content_type.split("/")[1]
            key = f"{image_prefix}{str(image_id)}.{extension}"
            self.s3.upload_fileobj(image, self.BUCKET_NAME, key)
        
        except Exception as error:
            logger.error(f"Error while uploading image: {error}")
            raise HTTPException(status_code=400, detail="Error while uploading image")

    def check_image_exist(self, image, image_prefix):
        objects = self.s3.list_objects_v2(Bucket=self.BUCKET_NAME, Prefix=image_prefix + image)
        if objects['KeyCount'] > 0:
            return True
        return False

    def delete_image_s3(self, image, image_prefix):
        extension = EXTENSION
        self.s3.delete_object(Bucket=self.BUCKET_NAME, Key= image_prefix + image + '.' + extension)
        return True
    
    def move_image(self, image, image_prefix):
        extension = EXTENSION
        source = {
            'Bucket': self.BUCKET_NAME,
            'Key': 'trash/' + image + '.' + extension
        }
        destination = image_prefix + image + '.' + extension
        self.s3.copy_object(Bucket=self.BUCKET_NAME, CopySource=source, Key=destination)
        self.s3.delete_object(Bucket=self.BUCKET_NAME, Key=source['Key'])
        return True
    
    def presigned_url(self, img_id: str,image_prefix: str, extension: str=EXTENSION):
        file_name = img_id + '.' + extension if extension else img_id
        url_get = self.s3v4.generate_presigned_url('get_object',
                                            Params={'Bucket': self.BUCKET_NAME, 'Key': image_prefix + file_name},
                                            ExpiresIn= 3600)
        return url_get
    
    def get_image(self, url):
        response = requests.get(url)

        if response.status_code != 200:
            raise HTTPException(f"Error downloading Image From S3")
        
        return response