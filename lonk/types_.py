from typing import Any

from werkzeug import Response

Body = str | bytes | dict
Headers = dict[str, Any] | list[tuple[str, Any]]
FlaskResponse = (
    Response
    | Body  # body
    | tuple[Body, int]  # body, status
    | tuple[Body, Headers]  # body, status
    | tuple[Body, int, Headers]  # body, status
)
