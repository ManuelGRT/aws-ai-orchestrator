# pylint: disable= too-few-public-methods
from functools import lru_cache

from pydantic import BaseSettings


class APISettings(BaseSettings):
    """
    Contains all global variables.
    """
    app_name: str = "Upscaling AI"
    app_name_underscore: str = app_name.replace(' ', '_')
    app_name_identifier: str = "upscaling ai"
    app_description: str = "Artificial Intelligence Upscaling Microservice"

    api_current_version: str = "1.0"
    api_credentials_id: str = f"Api{app_name_identifier.capitalize()}CredentialsV1"

    @staticmethod
    @lru_cache()
    def get_settings():
        """
        Caches all global variables.
        :return: APISettings class object cached
        """
        return APISettings()
