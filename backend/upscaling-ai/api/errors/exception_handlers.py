import http
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
from api.schemas.persistance import OrchestratorApiPersistance
from api.routers.logging import LoggingManager

logger = structlog.getLogger(__name__)

TIMESTAMP_EXCEPTION_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


def __get_timestamp_exception_format():
    """
    Returns timestamp format '%d/%b/%Y:%H:%M:%S %z' for exceptions.
    :return: string timestamp
    """
    return f"{datetime.strftime(datetime.now(timezone.utc), TIMESTAMP_EXCEPTION_FORMAT)}"


def __get_mail_format(message: str, log_level: str) -> str:
    """
    Formats the mail message for each exception
    :param message: a message string to include within mail
    :param log_level: log level string, the same level of logger output
    :return: a dict message formatted as string
    """
    message_formatted = {"log_level": log_level.upper(), "message": message}
    return message_formatted.__str__()


# pylint: disable= import-outside-toplevel
# pylint: disable= protected-access
def validate_required_fields(request_body, input_model, exc):
    """
    Tests if the post request received contains all the not optional fields from the schema, if there are any missing
    fields they will be added to a dictionary with their description.
    :param request_body: request_body
    :param input_model: Schema
    :return: list of strings
    """

    import typing

    optional_parameters: typing.List[str] = [
    ]
    conflicting_fields = {}
    missing_fields = {}
    wrong_type_fields = {}
    for item in input_model.__fields__:
        if item not in optional_parameters:
            # Checks missing fields
            if item not in request_body:
                missing_fields[item] = input_model.__fields__[item].field_info.description
                continue

        # Checks wrong type
        if isinstance(request_body[item], input_model.__fields__[item].type_):
            # Filter for date types in the schema, without this condition if the field is a date and is introduced as
            # a string that is parsed with a validator it would show a message of invalid format when another validation
            # error is detected.
            if f'-> {item}' not in str(exc):
                continue
            expected_type = input_model.__fields__[item].type_
            wrong_type_fields[item] = f'Expected : {expected_type} , Received : {request_body[item]} '

    if missing_fields:
        conflicting_fields['missing_required_fields'] = missing_fields
    if wrong_type_fields:
        conflicting_fields['wrong_type_fields'] = wrong_type_fields

    return conflicting_fields


async def validation_exception_handler(request, exc):
    """
    Handles all validation error exceptions and returns a custom response.
    :param request: request object
    :param exc: exception object
    :return: custom response in json format
    """

    http_bad_request_code = status.HTTP_400_BAD_REQUEST
    detected_wrong_fields = None

    for route in request.scope['router'].routes:
        if route.path:
            if re.match(route.path_regex, request.scope['path']):
                response_model = route.body_field.type_

                # Generates a string with info from the fields that generated the error.
                detected_wrong_fields = validate_required_fields(exc.body, response_model, exc)
    if detected_wrong_fields:
        http_bad_request_string = "Errors detected on the following fields: \n" \
                                  + str(detected_wrong_fields) + '\n Other validation errors:  ' + str(exc)
    else:
        http_bad_request_string = 'Bad request, ' + str(exc)

    errors = ErrorResponseErrors(code=http_bad_request_code,
                                          message=http_bad_request_string,
                                          rootCause=str(exc))
    str_traceback = traceback.format_exc()
    logger.warning(http_bad_request_string,
                   traceback=str_traceback)

    return JSONResponse(
        status_code=http_bad_request_code,
        content=ErrorResponse(code=http_bad_request_code, type=str(type(exc)),
                                       application=APISettings.get_settings().app_name_underscore,
                                       timestamp=__get_timestamp_exception_format(),
                                       errors=[errors]
                                       ).__dict__
    )


async def exception_handler(request, exc):
    """
    Handles all uncontrollable error exceptions and returns a custom response.
    :param request: request object
    :param exc: exception object
    :return: custom response in json format
    """
    http_internal_server_error_request_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    http_internal_server_error_request_string = "Internal Server Error"

    errors = ErrorResponseErrors(code=http_internal_server_error_request_code,
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
                                       timestamp=__get_timestamp_exception_format(),
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

    errors = ErrorResponseErrors(code=http_error_request_code,
                                          message=http_error_request_string)
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
        data_api=OrchestratorApiPersistance(
            request_id=context.get(header_keys.HeaderKeys.request_id),
            api_id="orchestrator_ai_api",
            image_id=image_id,
            response_latency=int(response_time*1000),
            request_datetime=datetime.utcnow().isoformat(),
            http_method=request.method,
            resource_path=str(request.url.path),
            status=http_error_request_code,
            error_message=str(exc.detail)
        )
    )
    
    return JSONResponse(
        status_code=http_error_request_code,
        content=ErrorResponse(code=http_error_request_code, type=str(type(exc)),
                                       application=APISettings.get_settings().app_name_underscore,
                                       timestamp=__get_timestamp_exception_format(),
                                       errors=[errors]
                                       ).__dict__,
        background=background_tasks
    )
