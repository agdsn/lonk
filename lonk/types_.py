from typing import Union, Any

from werkzeug import Response

Body = Union[str, bytes, dict]
Headers = Union[dict[str, Any], list[tuple[str, Any]]]
FlaskResponse = Union[
    Response,
    Body,  # body
    tuple[Body, int],  # body, status
    tuple[Body, Headers],  # body, status
    tuple[Body, int, Headers],  # body, status
]
