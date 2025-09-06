import logging
import os
import boto3
from fastapi import APIRouter, Depends, HTTPException, Request
import requests
from api.utils import commons as utils_commons
from api.services import auth_service
from api.utils.database import Database
from sqlmodel import Session
from api.utils.auth_api_requests import Authentication

# from aws_xray_sdk.core import xray_recorder

router = APIRouter()

logger = logging.getLogger(__name__)

database = Database()

COGNITO_DOMAIN = "https://cg-orchestrator-ai.auth.eu-west-1.amazoncognito.com"
CLIENT_ID = "vgn4lkl90bot0ptm58dr7tanu"
USERNAME = "fakeuser"
PASSWORD = "FakeUser123!"

#################
# AUTHORIZATION
#################
@router.get("/authorize-v1",
             responses=utils_commons.RESPONSES,
             name="Authenticate user")
def create_step(request: Request):
    """
    Create Step
    :param input: Input body

    :return: 
    """

    '''
    # with xray_recorder.in_segment('authuser'):
    auth_process = Authentication()
    response_auth = auth_process.get_auth_token()
    result = {}
    if response_auth and "access_token" in response_auth:
        result["token"] = response_auth["access_token"]
    else:
        # log or raise a proper exception with context
        raise HTTPException(status_code=404, detail="Failed to retrieve access_token from response_auth")
    # result = auth_service.process_input(session, request)
    return result
    '''

    url = f"{COGNITO_DOMAIN}/oauth2/token"
    data = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "username": USERNAME,
        "password": PASSWORD,
        "scope": "openid"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        return {"id_token": response.json().get("id_token")}
    else:
        raise HTTPException(status_code=401, detail=f"Login failed: {response.text}")


COGNITO_REGION = "eu-west-1"
# USER_POOL_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID")

cog = boto3.client("cognito-idp", region_name=COGNITO_REGION)

@router.get("/authorize")
def login(request: Request):
    try:
        logger.info("Starting authentication process")
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