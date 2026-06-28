import json
import os
from typing import Any, Optional

import boto3
import structlog
from botocore.exceptions import ClientError

logger = structlog.get_logger()

_secrets_cache: dict[str, Any] = {}


def get_secret(
    secret_name: str,
    secret_path: Optional[str] = None,
    region_name: str = "us-east-1",
) -> str:
    """
    Retrieve a secret from AWS Secrets Manager.

    Args:
        secret_name: Name/path of the secret (e.g., "posthog_api_key")
        secret_path: Full path in Secrets Manager (e.g., "app-name/environment/secret-name")
                     If not provided, uses secret_name as-is
        region_name: AWS region

    Returns:
        Secret value as string

    Raises:
        ValueError: If secret not found or value is empty
        ClientError: If AWS API fails
    """
    full_secret_name = secret_path or secret_name

    # Check cache
    if full_secret_name in _secrets_cache:
        return _secrets_cache[full_secret_name]

    try:
        client = boto3.client("secretsmanager", region_name=region_name)
        response = client.get_secret_value(SecretId=full_secret_name)

        if "SecretString" in response:
            secret_value = response["SecretString"]
        else:
            secret_value = response["SecretBinary"]

        # Cache the value
        _secrets_cache[full_secret_name] = secret_value

        logger.info(
            "secret_retrieved",
            secret_name=full_secret_name,
            cached=True,
        )
        return secret_value

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error(
            "failed_to_retrieve_secret",
            secret_name=full_secret_name,
            error_code=error_code,
            error_message=str(e),
        )
        raise ValueError(
            f"Failed to retrieve secret '{full_secret_name}': {error_code}"
        ) from e
    except Exception as e:
        logger.error(
            "unexpected_error_retrieving_secret",
            secret_name=full_secret_name,
            error=str(e),
        )
        raise


def get_secret_json(
    secret_name: str,
    secret_path: Optional[str] = None,
    region_name: str = "us-east-1",
) -> dict[str, Any]:
    """
    Retrieve a JSON secret from AWS Secrets Manager.

    Args:
        secret_name: Name/path of the secret
        secret_path: Full path in Secrets Manager
        region_name: AWS region

    Returns:
        Parsed JSON as dict
    """
    secret_value = get_secret(secret_name, secret_path, region_name)
    try:
        return json.loads(secret_value)
    except json.JSONDecodeError as e:
        logger.error(
            "failed_to_parse_json_secret",
            secret_name=secret_path or secret_name,
            error=str(e),
        )
        raise ValueError("Secret is not valid JSON") from e


def get_secret_or_env(
    env_var_name: str,
    secret_name: Optional[str] = None,
    secret_path: Optional[str] = None,
    region_name: str = "us-east-1",
) -> str:
    """
    Get secret from AWS Secrets Manager, fallback to environment variable.

    Useful for local development where AWS access may not be available.

    Args:
        env_var_name: Environment variable name to check first
        secret_name: Name/path of the secret in AWS
        secret_path: Full path in Secrets Manager
        region_name: AWS region

    Returns:
        Secret value from AWS or environment

    Raises:
        ValueError: If neither AWS secret nor env var found
    """
    # Try environment variable first (for local dev)
    env_value = os.environ.get(env_var_name)
    if env_value:
        logger.info(
            "using_environment_variable",
            env_var=env_var_name,
        )
        return env_value

    # Try AWS Secrets Manager
    try:
        return get_secret(secret_name or env_var_name, secret_path, region_name)
    except ValueError as e:
        logger.error(
            "secret_not_found_in_aws_or_env",
            env_var=env_var_name,
            secret_name=secret_name or env_var_name,
        )
        raise ValueError(
            f"Secret not found in AWS Secrets Manager or environment variable '{env_var_name}'"
        ) from e


def clear_cache() -> None:
    """Clear the secrets cache."""
    _secrets_cache.clear()
    logger.info("secrets_cache_cleared")
