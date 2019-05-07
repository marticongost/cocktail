"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import (
    Any,
    IO,
    Iterable,
    List,
    Mapping,
    Set,
    Sequence,
    Union
)
import json
import csv

import cherrypy

from cocktail.jsonutils import json_data
from cocktail.schema import (
    Member,
    Coercion,
    Collection,
    Record,
    Reference,
    Schema
)


class Default:
    pass

default = Default()

Payload = Union[str, bytes, IO]


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

    def iter_bodies(self) -> Iterable['RequestBody']:
        """Iterates over all the distinct specifications contained within this
        request body specification.

        Most request body definitions contain a single specification,
        represented by their own object; the notable exception is the
        `MultipleRequestBodies` class, which selects an actual `RequestBody` to
        activate based on the request's Content-Type. This method is a
        convenience to enumerate the actual `RequestBody` objects that can be
        used to serve a request.
        """
        yield self

    def matches_type(self, type: str) -> bool:
        """Determines whether the request body can serve a request with the
        given Content-Type.
        """
        return not self.types or type.split(";", 1)[0] in self.types

    def process(self) -> Any:
        """Attempt to process the request's body, extracting and possibly
        parsing its data.

        If the request's Content-Type doesn't match the request body
        specification (as specified by `matches_type`) and the body is
        `required`, the method will raise a 415 HTTP error.
        """
        req_type = cherrypy.request.headers.get("Content-Type")

        if self.matches_type(req_type):
            return self.get_data()
        elif self.required:
            raise cherrypy.HTTPError(415, "Unsupported request type")
        else:
            return None

    def get_payload(self) -> Payload:
        """Extract the raw data from the request's body."""
        length = int(cherrypy.request.headers["Content-Length"])
        payload = cherrypy.request.body.read(length)

        if self.encoding:
            payload = payload.decode(self.encoding)

        return payload

    def get_data(self) -> Any:
        """Process the request's body, extracting and possibly parsing its
        data.
        """
        payload = self.get_payload()
        data = self.parse(payload)

        if self.schema and self.coercion:
            data = self.schema.coerce(data, self.coercion)

        return data

    def parse(self, payload: Payload) -> Any:
        """Parse a payload extracted from the request's body."""

        if self.schema:
            payload = self.schema.parse(payload)

        return payload


class MultipleRequestBodies(RequestBody):

    bodies: Sequence[RequestBody] = ()

    def __init__(
        self,
        bodies: Union[Default, Sequence[RequestBody]] = default,
        required: Union[bool, Default] = default,
    ):
        super().__init__(required=required)
        if bodies is not default:
            self.bodies = list(bodies)

    def iter_bodies(self) -> Iterable[RequestBody]:
        yield from self.bodies

    def process(self) -> Any:

        req_type = cherrypy.request.headers.get("Content-Type")

        for body in self.bodies:
            if body.matches_type(req_type):
                return body.get_data()

        if self.required:
            raise cherrypy.HTTPError(415, "Unsupported request type")

        return None


class PlainTextBody(RequestBody):

    types = {"text/plain"}
    encoding = "utf-8"


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

    def parse(self, payload: str) -> json_data:

        data = json.loads(payload, **self.parser_options)

        if self.schema and self.process_json:
            data = self.schema.from_json_value(data, **self.import_options)

        return data


class CSVBody(RequestBody):

    types = {"text/csv"}
    encoding = "utf-8"
    reader_options: Mapping[str, Any] = {}
    parse_rows: bool = True
    aggregate_rows: bool = True
    columns: List[Member] = None

    def __init__(
        self,
        columns: Union[List[Member], Default] = default,
        reader_options: Mapping[str, Any] = default,
        parse_rows: Union[bool, Default] = default,
        aggregate_rows: Union[bool, Default] = default,
        **kwargs
    ):
        super().__init__(**kwargs)

        if self.schema:
            assert isinstance(self.schema, Collection)

        assert self.encoding

        if columns is not default:
            self.columns = columns

        if self.columns is None and self.schema:
            items_schema = None

            if isinstance(self.schema.items, Reference):
                items_schema = self.schema.items.type
            elif isinstance(self.schema.items, Record):
                items_schema = self.schema.items.record_schema
            elif isinstance(self.schema.items, Schema):
                items_schema = self.schema.items

            if isinstance(items_schema, Schema):
                self.columns = items_schema.ordered_members()

        if reader_options is not default:
            self.reader_options = reader_options

        if parse_rows is not default:
            self.parse_rows = parse_rows

        if aggregate_rows is not default:
            self.aggregate_rows = aggregate_rows

    def get_payload(self) -> IO:
        return cherrypy.request.body

    def parse(self, payload: IO) -> Any:

        lines = (line.decode(self.encoding) for line in payload)
        reader = csv.reader(lines, **self.reader_options)

        if self.schema and self.schema.items and self.parse_rows:
            rows = map(self.parse_row, reader)
        else:
            rows = reader

        if self.aggregate_rows or self.coercion is not Coercion.NONE:
            rows = list(rows)

        return rows

    def parse_row(self, row: dict) -> Any:
        return {
            member.name: member.parse(value)
            for value, member in zip(row, self.columns)
        }

