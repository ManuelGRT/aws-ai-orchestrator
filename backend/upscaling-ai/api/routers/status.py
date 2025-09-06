import logging

from api.schemas import status
from api.utils import commons as utils_commons

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()

#################
# API STATUS
#################
@router.get("/status",
            response_model=status.StatusOutput,
            responses=utils_commons.RESPONSES,
            name="Get Verificacion Digital Autos API Status")
def status():
    """
    Returns API status.
    :return: UP status in json format
    """
    logger.info("Status endpoint reached correctly")
    return {"status": "UP"}

