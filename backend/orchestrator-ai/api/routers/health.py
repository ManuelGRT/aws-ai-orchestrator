import logging

from api.schemas import status
from api.utils import commons as utils_commons

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()

#################
# API STATUS
#################
@router.get("/health",
            response_model=status.HealthOutput,
            responses=utils_commons.RESPONSES,
            name="Get Health")
def health():
    """
    Returns API health.
    :return: UP status in json format
    """
    logger.info("Status endpoint reached correctly")
    return {"health": "OK"}

