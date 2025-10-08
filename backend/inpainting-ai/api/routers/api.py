from fastapi import APIRouter
from api.routers import logging
from api.routers import health as health_router
from api.routers import inpainting as inpainting_router


api_router = APIRouter()

# Common router
api_router.include_router(health_router.router)

# API v1
api_router.include_router(inpainting_router.router)

# Logging configuration
api_router.include_router(logging.router)
