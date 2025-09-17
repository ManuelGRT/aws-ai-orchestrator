# pylint: disable= no-name-in-module, missing-class-docstring, missing-function-docstring, no-self-argument,
# pylint: disable= no-self-use, too-few-public-methods
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from api.config.api_settigs import APISettings

class ErrorResponseErrors(BaseModel):
    code: str = Field(description="HTTP code error", example="500")
    message: Optional[str] = Field(description="Specific exception message", example="Internal Server Error")
    # component: Optional[str] = Field(description="Component which generates the error", example=None)
    rootCause: Optional[str] = Field(description="Root cause error description",
                                     example="1 validation error for Request\nbody -> values -> platform\n  "
                                             "field required (type=value_error.missing)")

class ErrorResponse(BaseModel):
    code: str = Field(description="HTTP code error", example="500")
    message: str = Field("An error occurred while making the request", Literal=True,
                         description="Static standard message", example="An error occurred while making the request")
    type: str = Field(description="Error type represented by its class", example="<class 'KeyError'>")
    # context: Optional[str] = Field(description="Execution context of the error", example=None)
    # exception: Optional[str] = Field(description="Generic exception description", example=None)
    application: str = Field(description="Application name", example=APISettings.get_settings().app_name)
    timestamp: str = Field(
        description="Date in CLF (https://httpd.apache.org/docs/current/logs.html#common) "
                    "with this specific format: %d/%b/%Y:%H:%M:%S %z",
        example="17/Aug/2021:10:55:24 +0000")
    errors: Optional[List[ErrorResponseErrors]] = Field(description="Detailed errors information")

    @validator('errors')
    def serialize_errors(cls, errors):
        return [error.__dict__ for error in errors]
