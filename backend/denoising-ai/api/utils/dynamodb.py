import os
from api.utils.commons import get_secret
import boto3
import time

from fastapi import HTTPException
from api.routers.logging import LoggingManager
from api.schemas.persistance import DenoisingApiPersistance

# ENV_SECRET_ARN = os.getenv("ENV_SECRET_ARN")

class DynamoDB:
    def __init__(self):
        # self.secret = get_secret(ENV_SECRET_ARN)
        # self.DYNAMODB_TABLE = self.secret['DYNAMODB_TABLE']
        self.DYNAMODB_TABLE = "orchestrator-ai-api-info"  # Replace with your actual table name

        # AWS Clients
        self.db    = boto3.resource('dynamodb', region_name="eu-west-1")
        self.table = self.db.Table(self.DYNAMODB_TABLE)

    def upload_api_persistance(self, data_api: DenoisingApiPersistance, logger: LoggingManager):
        try:
            logger.info(f"Saving api info in DynamoDB: {data_api.dict()}")
            self.table.put_item(Item=data_api.dict())
            logger.info(f"Api info saved successfully in DynamoDB")

        except Exception as e:
            logger.error(f"Error saving api info in DynamoDB: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error saving api info in DynamoDB: {str(e)}")
        
    def upload_token(self, code:str ,token: str, expire_time: int):
        try:
            ttl = int(time.time()) + expire_time  # Expira en 1 hora
            data = {"code": code, "token": token, "ttl": ttl}

            self.table.put_item(Item=data)
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al guardar el token en DynamoDB: {str(e)}")
    
    def get_token(self, code: str):
        response = self.table.get_item(Key={"code": code})
        item = response.get("Item")
        
        if not item:
            raise HTTPException(status_code=404, detail="Token no encontrado")

        return item.get("token")