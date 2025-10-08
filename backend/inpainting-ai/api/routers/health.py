import logging

from api.schemas import health
from api.utils import commons as utils_commons

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()

#################
# API STATUS
#################
@router.get("/health",
            response_model=health.HealthOutput,
            responses=utils_commons.RESPONSES,
            name="Get Health")
def status():
    """
    Returns API status.
    :return: UP status in json format
    """
    logger.info("Health endpoint reached correctly")
    return {"health": "OK"}

