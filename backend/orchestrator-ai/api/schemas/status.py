# pylint: disable= no-name-in-module, missing-class-docstring, too-few-public-methods
from pydantic import BaseModel
from pydantic import Field


class HealthOutput(BaseModel):
    health: str = Field(..., description="API health description", example="UP")
