import logging

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from starlette.middleware import Middleware

from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

# from aws_xray_sdk.core import patch_all

from api.config.api_settigs import APISettings
from api.config import exception_handlers
from api.routers.api import api_router

logger = logging.getLogger(__name__)


def get_application(settings: APISettings) -> FastAPI:
    """
    Configures FastAPI application.
    :param settings: APISettings object
    :return: FastAPI object
    """
    middlewares = [
        Middleware(
            RawContextMiddleware,
            plugins=(
                plugins.RequestIdPlugin(),
            ),
        ),
    ]

    # Root API declaration
    application = FastAPI(title=settings.app_name,
                          description=settings.app_description,
                          middleware=middlewares, 
                          docs_url=None, redoc_url=None, openapi_url=None )
    #, docs_url=None, redoc_url=None

    # Add error for exception handlers
    application.add_exception_handler(Exception, exception_handlers.exception_handler)
    application.add_exception_handler(HTTPException, exception_handlers.http_exception_handler)

    # Add CORS headers
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )                              

    # Include routes with api versioning
    # Build all api versions included in api_router variable
    application.include_router(api_router)

    print("Application created successfully.")

    return application


def custom_openapi_schema():  # pragma: no cover
    """
    Overrides Openapi schema.
    :return: openapi_schema object
    """
    # Schema cache
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=APISettings.get_settings().app_name,
        version=APISettings.get_settings().api_current_version,
        description=APISettings.get_settings().app_description,
        routes=app.routes,
    )

    # Delete unused schemas
    if openapi_schema["components"]["schemas"]["ValidationError"] is not None:
        del openapi_schema["components"]["schemas"]["ValidationError"]
    if openapi_schema["components"]["schemas"]["HTTPValidationError"] is not None:
        del openapi_schema["components"]["schemas"]["HTTPValidationError"]

    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            # Look for the error 422 and delete it
            if openapi_schema["paths"][path][method]["responses"].get("422"):
                del openapi_schema["paths"][path][method]["responses"]["422"]
            # Replace default http validation error with custom response
            if openapi_schema["paths"][path][method]["responses"]["400"]["content"][
                "application/json"
            ]["schema"]["$ref"]:
                openapi_schema["paths"][path][method]["responses"]["400"]["content"][
                    "application/json"]["schema"]["$ref"] = "#/components/schemas/ErrorResponse"
            if openapi_schema["paths"][path][method].get("description"):
                del openapi_schema["paths"][path][method]["description"]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = get_application(APISettings.get_settings())
app.openapi = custom_openapi_schema

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=True, server_header=False)
    custom_openapi_schema()