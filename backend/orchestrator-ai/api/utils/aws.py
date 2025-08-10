import os
import json
import logging

from functools import lru_cache
from typing import Tuple

import boto3
# from aws_xray_sdk.core import xray_recorder
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig

from api.config.api_settigs import APISettings

import aws_encryption_sdk
from aws_encryption_sdk.identifiers import CommitmentPolicy

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_secrets_manager_auth() -> Tuple[str, str]:
    """
    Returns username and password from AWS Secrets Manager or from cache.
    :return: username and password as Tuple
    """
    # MODEL_LOGS_BUCKET environment variable is reused to check localhost execution
    if os.environ.get("MODEL_LOGS_BUCKET", None) is None:
        logger.info("It is a local environment, there is no connection to AWS, using empty auth")
        return "local", "admin"

    secrets_manager_client = boto3.client('secretsmanager')
    api_credentials = json.loads(secrets_manager_client.get_secret_value(
        SecretId=APISettings.get_settings().api_credentials_id)['SecretString'])
    return api_credentials['username'], api_credentials['password']


def get_secret(secret_name):
    """
    Returns a secret stored in SecretsManager.
    :return: Secret value
    """
    # with xray_recorder.in_segment('get_secret'):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager'
    )

    cache = SecretCache(config=SecretCacheConfig(), client=client)
    secret = json.loads(cache.get_secret_string(secret_name))

    return secret


def get_cipher_value(plain_value):
    """
        Returns the encrypted value using KMS key
        :return: Encrypted value
        """
    # TODO: Revisar tiempos de respuesta y hacerlo singleton
    crypt_client = aws_encryption_sdk.EncryptionSDKClient(
        commitment_policy=CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT
    )

    kms_key_provider = aws_encryption_sdk.StrictAwsKmsMasterKeyProvider(key_ids=[
        os.environ.get('ENCRYPTION_KEY_ARN')
    ])

    cipher_value = crypt_client.encrypt(
        source=plain_value,
        key_provider=kms_key_provider
    )

    return cipher_value[0]