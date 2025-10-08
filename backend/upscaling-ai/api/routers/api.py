from fastapi import APIRouter

from api.config.api_settigs import APISettings
from api.routers import logging
from api.routers import health as health_router
from api.routers import upscaling as upsacling


api_router = APIRouter()

# Common router
api_router.include_router(health_router.router)

# API v1
api_router.include_router(upsacling.router)

# Logging configuration
api_router.include_router(logging.router)
