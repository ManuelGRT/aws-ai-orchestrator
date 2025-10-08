from pydantic import BaseModel
from pydantic import Field


class HealthOutput(BaseModel):
    health: str = Field(..., description="API health description", example="OK")
