from fastapi import APIRouter

from api.config.api_settigs import APISettings
from api.routers import logging
from api.routers import health as health_router
from api.routers import orchestrator as orchestrator_router
from api.routers import auth as auth_router


api_router = APIRouter()

# Common router
api_router.include_router(health_router.router)

# API router
api_router.include_router(orchestrator_router.router)

# Auth router
api_router.include_router(auth_router.router)

# Logging configuration
api_router.include_router(logging.router)
