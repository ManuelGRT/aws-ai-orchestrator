import re
from datetime import datetime
from datetime import timezone
import traceback
from starlette_context import context, header_keys
import structlog

from fastapi import BackgroundTasks, HTTPException, status, Request
from fastapi.responses import JSONResponse

from api.config.api_settigs import APISettings
from api.schemas.errors import ErrorResponse
from api.schemas.errors import ErrorResponseErrors

from api.utils.dynamodb import DynamoDB
from api.schemas.persistance import InpantingApiPersistance
from api.routers.logging import LoggingManager

logger = structlog.getLogger(__name__)

TIMESTAMP_EXCEPTION_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


async def exception_handler(request, exc):
    """
    Handles all uncontrollable error exceptions and returns a custom response.
    :param request: request object
    :param exc: exception object
    :return: custom response in json format
    """
    http_internal_server_error_request_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    http_internal_server_error_request_string = "Internal Server Error"

    errors = ErrorResponseErrors(code=str(http_internal_server_error_request_code),
                                          message=http_internal_server_error_request_string,
                                          rootCause=str(exc))
    log_level = "error"
    str_traceback = traceback.format_exc()
    logger.error(http_internal_server_error_request_string,
                 traceback=traceback.format_exc(),
                 # no-request-id for errors which raise out of http context
                 request_id=request.headers.get("x-request-id", "no-request-id"))

    return JSONResponse(
        status_code=http_internal_server_error_request_code,
        content=ErrorResponse(code=http_internal_server_error_request_code, type=str(type(exc)),
                                       application=APISettings.get_settings().app_name_underscore,
                                       timestamp=f"{datetime.strftime(datetime.now(timezone.utc), TIMESTAMP_EXCEPTION_FORMAT)}",
                                       errors=[errors]
                                       ).__dict__
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handles all uncontrollable http error exceptions and returns a custom response.
    :param request: request object
    :param exc: exception object
    :return: custom response in json format
    """
    http_error_request_code = exc.status_code
    http_error_request_string = exc.detail

    errors = ErrorResponseErrors(code=str(http_error_request_code),
                                          message=http_error_request_string,
                                          rootCause="")
    log_level = "warning"
    str_traceback = traceback.format_exc()
    logger.warning(http_error_request_string,
                   traceback=traceback.format_exc())
    
    background_tasks = BackgroundTasks()
    logger.info("Sending error api to dynamodb...")

    image_id = exc.headers.get("image_id") if exc.headers else None
    response_time = exc.headers.get("response_time") if exc.headers else 0

    dynamodb = DynamoDB()
    background_tasks.add_task(
        dynamodb.upload_api_persistance,
        logger=LoggingManager(context.get(header_keys.HeaderKeys.request_id), image_id),
        data_api=InpantingApiPersistance(
            request_id=context.get(header_keys.HeaderKeys.request_id),
            api_id="inpainting_ai_api",
            image_id=image_id,
            response_latency=int(response_time*1000),
            request_datetime=datetime.utcnow().isoformat(),
            http_method=request.method,
            resource_path=str(request.url.path),
            status=str(http_error_request_code),
            error_message=str(exc.detail)
        )
    )
    
    return JSONResponse(
        status_code=http_error_request_code,
        content=ErrorResponse(code=str(http_error_request_code), type=str(type(exc)),
                                       application=APISettings.get_settings().app_name_underscore,
                                       timestamp=f"{datetime.strftime(datetime.now(timezone.utc), TIMESTAMP_EXCEPTION_FORMAT)}",
                                       errors=[errors]
                                       ).__dict__,
        background=background_tasks
    )
