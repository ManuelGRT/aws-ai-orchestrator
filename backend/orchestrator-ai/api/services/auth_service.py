from fastapi import HTTPException
from sqlmodel import Session, select, or_
from api.utils.auth_api_requests import Authentication
from fastapi import HTTPException, Request

import re

# from api.utils.dynamodb import DynamoDB

auth_process = Authentication()

# dynamodb = DynamoDB()

def verify_token(Code: str, request: Request):
    token = request.headers.get("Authorization")

    # Verificar si el token existe y es válido
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    
    token = token.replace("Bearer ", "")

   # token_dynamo = dynamodb.get_token(urlCode)
   # if (token != token_dynamo):
   #     raise HTTPException(status_code=401, detail="Token inválido o expirado")