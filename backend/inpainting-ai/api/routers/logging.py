# pylint: disable= unused-argument
from datetime import datetime, timezone
import logging
import time

from typing import Any
from typing import MutableMapping
import structlog
from starlette_context import context

from fastapi import APIRouter

router = APIRouter()

logger = logging.getLogger("app_logger")

@router.on_event("startup")
async def configure_logging() -> None:
    """
    Configures logging format at API startup.
    """

    def add_app_context(
            logger: logging.Logger,
            method_name: str,
            event_dict: MutableMapping[str, Any],
    ) -> MutableMapping[str, Any]:
        """
        Adds request context into event_dict log.
        :param logger: logger object class
        :param method_name: logger method name
        :param event_dict: logger event in dict format
        :return: event_dict object updated
        """
        if context.exists():
            event_dict.update(context.data)
        return event_dict

    def upper_log_level(
            logger: logging.Logger,
            method_name: str,
            event_dict: MutableMapping[str, Any], ):
        """
        Transforms logger level in uppercase.
        :param logger: logger object class
        :param method_name: logger method name
        :param event_dict: logger event in dict format
        :return: event_dict object updated
        """
        event_dict["level"] = method_name.upper()
        return event_dict

    def add_epoch_timestamp_millis(
            logger: logging.Logger,
            method_name: str,
            event_dict: MutableMapping[str, Any], ):
        """
        Adds epoch timestamp with millisecond precision.
        :param logger: logger object class
        :param method_name: logger method name
        :param event_dict: logger event in dict format
        :return: event_dict object updated
        """
        event_dict["timestamp"] = round(time.time() * 1000)
        return event_dict

    shared_processors = [
        add_epoch_timestamp_millis,
        structlog.stdlib.add_log_level,
        upper_log_level,
        structlog.stdlib.add_logger_name,
        add_app_context,
    ]
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        # wrapper_class=structlog.stdlib.AsyncBoundLogger,  # Use AsyncBoundLogger for async logs
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        # processor=structlog.processors.JSONRenderer(),  # Used it for JSON log
        processor=structlog.dev.ConsoleRenderer(colors=False),
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


class LoggingManager():

    def __init__(self, request_id: str, image_id: str):
        self.logger = logging.getLogger(__name__)
        self.request_id = request_id
        self.image_id = image_id
    
    def info(self, message: str):
        timestamp = datetime.now(timezone.utc).isoformat()
        self.logger_body = f"request_id: {self.request_id} | image_id: {self.image_id}"

        self.logger.info(f"timestamp: {timestamp} | {self.logger_body} | logging_message: {message}")

    def error(self, message: str):
        timestamp = datetime.now(timezone.utc).isoformat()
        self.logger_body = f"request_id: {self.request_id} | image_id: {self.image_id}"
        self.logger.error(f"timestamp: {timestamp} | {self.logger_body} | logging_message: {message}")