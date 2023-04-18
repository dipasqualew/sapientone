import json
import os
import logging

from typing import Any, Callable, Literal, Optional

from pydantic.error_wrappers import ValidationError

LOGGING_SEVERITY = Literal["NOTICE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def log(severity: LOGGING_SEVERITY, content: dict[str, Any]):
    log_message = dict(
        severity=severity,
        **content,
    )

    print(json.dumps(log_message))

    return log_message


def get_logger(name: str, logging_level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)

    return logger


def get_env_var(env_var_name: str) -> str:
    env_var = os.environ.get(env_var_name)

    if not env_var:
        raise ValueError(f"Environment variable '{env_var_name}' not set")

    return env_var


def get_json_data(request: Any) -> dict[str, Any]:
    json_data = request.get_json()

    if not json_data:
        raise ValueError("No JSON data provided")

    return json_data


def make_response(
    data: Any,
    status_code: int = 200,
    headers: Optional[dict[str, str]] = None,
) -> Any:
    response_headers = {
        "Access-Control-Allow-Origin": "*",
    }

    response_headers.update(headers or {})

    return data, status_code, response_headers


def lambda_wrapper(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    def wrapper(request: Any) -> Any:
        # Set CORS headers for the preflight request
        if request.method == "OPTIONS":
            # Allows GET requests from any origin with the Content-Type
            # header and caches preflight response for an 3600s
            headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "Authorization, Content-Type",
                "Access-Control-Max-Age": "3600",
            }

            return ("", 204, headers)

        api_key = get_env_var("SAPIENTONE_API_KEY")
        provided_key = request.headers.get("Authorization")

        if api_key != provided_key:
            return make_response({"error": "Invalid API key"}, 401)

        try:
            response = func(request)
            return response
        except ValidationError as exc:
            response_data = {"error": {"type": "Validation Error", "metadata": exc.errors()}}

            return make_response(response_data, 400)

        except Exception:
            logging.exception("Error at top level")

            response_data = {"error": {"type": "Internal Server Error", "metadata": {}}}

            return make_response(response_data, 500)

    return wrapper
