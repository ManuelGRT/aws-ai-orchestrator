import logging
import os
import requests
import base64
from api.utils.aws import get_secret

# ENV_SECRET_ARN = os.getenv("ENV_SECRET_ARN")
ENV_SECRET_ARN = "arn:aws:secretsmanager:eu-west-1:435772683141:secret:orchestrator-ai-api-env-qiCMIU"

logger = logging.getLogger(__name__)


class Authentication:

    def __init__(self):
        #self.secret = get_secret(ENV_SECRET_ARN)
        self.client_id = "4re8primihbnvn2kfjta15gpv8" # self.secret["COGNITO_CLIENT_ID"]
        self.secret_id = "1k2foicd02k943831nmnmq5ld6ra4to5mau03f401u116vfummt8" #self.secret["COGNITO_SECRET_ID"]
        self.host_cognito = "https://cg-orchestrator-ai.auth.eu-west-1.amazoncognito.com/oauth2/token?grant_type=client_credentials" #self.secret["COGNITO_HOST_ID"]

    def get_auth_token(self):
        auth_b64 = base64.b64encode(f"{self.client_id}:{self.secret_id}".encode())
        payload = {}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f"Basic {auth_b64.decode('utf-8')}"
            }

        logger.info("Llamando a cognito para solicitar el token...")
        logger.info(f"Cognito params: {self.host_cognito}, {self.client_id}, {self.secret_id}")
        response = requests.post(self.host_cognito, headers=headers, data=payload)
        logger.info(f"Llamando a cognito finalizada: {response.json()}")
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error al obtener token: status={response.status_code}, body={response.text}")
            return None
