import logging
from api.schemas import health
from api.utils import commons as utils_commons
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()

############
# API HEALTH
############
@router.get("/health",
            response_model=health.HealthOutput,
            responses=utils_commons.RESPONSES,
            name="Get API Health")
def health():
    logger.info("Health endpoint reached correctly")
    return {"health": "OK"}