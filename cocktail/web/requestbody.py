"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import (
    Any,
    Mapping,
    Set,
    Union
)
import json

import cherrypy

from cocktail.schema import Member, Coercion


class Default:
    pass

default = Default()


class RequestBody:
    """A specification for an expected request body."""

    types: Set[str] = None
    required: bool = True
    encoding: str = None
    schema: Member = None
    coercion: Coercion = Coercion.FAIL

    def __init__(
        self,
        types: Union[Set[str], None, Default] = default,
        required: Union[bool, Default] = default,
        schema: Union[Member, None, Default] = default,
        encoding: Union[str, None, Default] = default,
        coercion: Union[Coercion, Default] = default
    ):
        if types is not default:
            self.types = types

        if required is not default:
            self.required = required

        if schema is not default:
            self.schema = schema

        if encoding is not default:
            self.encoding = encoding

        if coercion is not default:
            self.coercion = coercion

    def matches_type(self, type: str) -> bool:
        return not self.types or type in self.types

    def process(self) -> Any:

        content_type = cherrypy.request.headers.get("Content-Type")

        if self.matches_type(content_type):
            length = int(cherrypy.request.headers["Content-Length"])
            payload = cherrypy.request.body.read(length)

            if self.encoding:
                payload = payload.decode(self.encoding)

            data = self._process_payload(payload)

            if self.schema and self.coercion:
                data = self.schema.coerce(data, self.coercion)

            return data

        elif self.required:
            raise cherrypy.HTTPError(415, "Unsupported request type")

        return None

    def _process_payload(self, payload: Union[bytes, str]) -> Any:

        if self.schema:
            payload = self.schema.parse(payload)

        return payload


class JSONBody(RequestBody):

    types = {"application/json"}
    encoding = "utf-8"
    parser_options = {}
    import_options = {}
    process_json = True

    def __init__(
        self,
        import_options: Mapping[str, Any] = None,
        process_json: Union[bool, Default] = default,
        **kwargs
    ):
        super().__init__(**kwargs)

        if import_options is not None:
            self.import_options = self.import_options.copy()
            self.import_options.update(import_options)

        if process_json is not default:
            self.process_json = process_json

    def _process_payload(
            self,
            payload: str) -> Union[dict, str, int, bool, None]:

        data = json.loads(payload, **self.parser_options)

        if self.schema and self.process_json:
            data = self.schema.from_json_value(data, **self.import_options)

        return data

