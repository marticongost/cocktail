"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Tuple,
    Union
)
import json

import yaml
import cherrypy

from cocktail.jsonutils import ExtensibleJSONEncoder

DEFAULT_ENCODING = "utf-8"

ResponseFormatter = Callable[[Any], Union[str, bytes]]

response_formatters: Dict[str, ResponseFormatter] = {
    "application/json": lambda data: json.dumps(data, cls=ExtensibleJSONEncoder),
    "application/x-yaml": lambda data: yaml.dump(data, sort_keys=False)
}


def split_response_type(content_type: str) -> Tuple[str, Optional[str]]:

    pos = content_type.rfind(";", 1)
    if pos == -1:
        return content_type, None

    mime_type = mime_type[:pos]
    rest = mime_type[pos + 1:].strip()
    if rest.startswith("charset="):
        charset = rest[len("charset="):]
        return mime_type, charset

    return mime_type, None


def format_response(
        data: Any,
        content_type: str = None,
        encoding: str = "auto") -> bytes:

    if not content_type:
        content_type = cherrypy.response.headers["Content-Type"]

    mime_type, charset = split_response_type(content_type)
    if encoding == "auto":
        charset = charset or DEFAULT_ENCODING
    else:
        charset = encoding

    formatter = response_formatters.get(mime_type)
    if formatter:
        data = formatter(data)

    if charset and isinstance(data, str):
        data = data.encode(charset)

    return data

