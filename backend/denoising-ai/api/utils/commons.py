from api.schemas.errors import ErrorResponse
import json
import boto3
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig


RESPONSES = {
    400: {'model': ErrorResponse},
    401: {'model': ErrorResponse},
    403: {'model': ErrorResponse},
    500: {'model': ErrorResponse}
}


def get_secret(secret_name):
    """
    Returns a secret stored in SecretsManager.
    :return: Secret value
    """
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager'
    )

    cache = SecretCache(config=SecretCacheConfig(), client=client)
    secret = json.loads(cache.get_secret_string(secret_name))

    return secret