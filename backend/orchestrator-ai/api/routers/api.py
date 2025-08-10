from fastapi import APIRouter

from api.config.api_settigs import APISettings
from api.routers import logging
from api.routers import status as status_router
from api.routers import image as image_v1
from api.routers import auth as auth_router


api_router = APIRouter()
TAG_COMERCIOS = "Comercios"


# Common router
api_router.include_router(status_router.router)

# API v1
api_router.include_router(image_v1.router)

api_router.include_router(auth_router.router)

# Logging configuration
api_router.include_router(logging.router)
