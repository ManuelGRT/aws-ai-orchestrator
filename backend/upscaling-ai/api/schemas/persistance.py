from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Union

class UpsaclingApiPersistance(BaseModel):
    """
    Data structure used to persist AI evaluation results for observability and monitoring.

    This model is primarily used for logging and storing granular evaluation data from
    each microservice involved in this ai model.

    Attributes:
        request_id (Optional[str]): Unique identifier for the specific request instance.
        api_id (Optional[str]): Identifier of the api involved.
        image_id (Optional[str]): Unique identifier for the image being processed.
        response_latency (Optional[int]): Request latency.
        request_datetime (Optional[str]): Specific datetime of the request.
        http_method (Optional[str]): Http method (GET, POST, DELETE...).
        resource_path (Optional[str]): Api endpoint path.
        status (Optional[str]): Status of the endpoint (200, 400, 500...).
        error_message (Optional[str]): In case it fails, error message.
    """
    request_id: Optional[str] = None
    api_id: Optional[str] = None
    image_id: Optional[str] = None
    response_latency: Optional[int] = None
    request_datetime: Optional[str] = None
    http_method: Optional[str] = None
    resource_path: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None