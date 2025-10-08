import logging
import os
import boto3
from fastapi import APIRouter, Depends, HTTPException, Request
import requests
from api.utils import commons as utils_commons
from api.utils.auth_api_requests import Authentication

router = APIRouter()

logger = logging.getLogger(__name__)

COGNITO_DOMAIN = "https://cg-orchestrator-ai.auth.eu-west-1.amazoncognito.com"
CLIENT_ID = "vgn4lkl90bot0ptm58dr7tanu"
USERNAME = "fakeuser"
PASSWORD = "FakeUser123!"

COGNITO_REGION = "eu-west-1"
# USER_POOL_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID")

cog = boto3.client("cognito-idp", region_name=COGNITO_REGION)

#################
# AUTHORIZATION
#################
@router.get("/authorize")
def login(request: Request):
    try:
        logger.info("Starting authentication process...")
        USER_POOL_CLIENT_ID = "vgn4lkl90bot0ptm58dr7tanu"
        resp = cog.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=USER_POOL_CLIENT_ID,
            AuthParameters={
                "USERNAME": USERNAME,
                "PASSWORD": PASSWORD
            },
        )
        auth = resp.get("AuthenticationResult")
        if not auth:
            raise HTTPException(status_code=401, detail="Credenciales inválidas o challenge pendiente")
        
        logger.info("Finishing authentication process")
        return {
            "id_token": auth["IdToken"],
            "access_token": auth["AccessToken"],
            "refresh_token": auth.get("RefreshToken"),
            "expires_in": auth["ExpiresIn"],
            "token_type": auth["TokenType"]
        }
    except cog.exceptions.NotAuthorizedException:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))