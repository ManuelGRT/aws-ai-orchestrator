from fastapi import APIRouter

from api.config.api_settigs import APISettings
from api.routers import logging
from api.routers import status as status_router
from api.routers import image as image_router
from api.routers import auth as auth_router


api_router = APIRouter()

# Common router
api_router.include_router(status_router.router)

# API router
api_router.include_router(image_router.router)

# Auth router
api_router.include_router(auth_router.router)

# Logging configuration
api_router.include_router(logging.router)
