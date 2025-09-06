# pylint: disable= no-name-in-module, missing-class-docstring, too-few-public-methods
from pydantic import BaseModel
from pydantic import Field


class StatusOutput(BaseModel):
    status: str = Field(..., description="API status description", example="UP")
