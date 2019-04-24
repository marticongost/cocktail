"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import (
    Any,
    Callable,
    Dict,
    Mapping,
    Optional,
    Sequence,
    Set,
    Type,
    Union
)
from abc import abstractmethod
from collections import ChainMap
import http.client
import json

import yaml
import cherrypy

from cocktail.events import Event
from cocktail.schema import Schema, Member, Coercion
from cocktail.controllers import request_property, get_parameter
from cocktail.yamlutils import yaml_template
from cocktail.pkgutils import get_full_name
from .handler import Handler, any_origin
from . import node
from .responsespec import ResponseSpec
from .requestbody import RequestBody
from .responseformats import format_response


class Method(Handler):
    """An HTTP method implementation for a `Node`."""

    responding = Event(
        doc="""
            An event triggered just before a method starts producing the
            response for the current HTTP request.

            Arguments, parameters and request bodies have already been
            processed at this point.
            """
    )

    cors_enabled: bool = True
    parameters: Sequence[Member] = []
    parameter_coercion: Coercion = Coercion.FAIL_IMMEDIATELY
    parameter_options: dict = {
        "errors": "ignore",
        "undefined": "set_default",
        "implicit_booleans": False
    }
    parameter_validation_options: dict = {}
    values: dict = {}
    request_body: RequestBody = None
    response_type: str = None
    responses: Mapping[int, Union[ResponseSpec, dict]] = ChainMap()
    format_response: bool = True
    response_encoding: Optional[str] = "utf-8"
    possible_errors: Set[Type[Exception]] = set()
    open_api: yaml_template = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Subclasses aggregate the values of Handler.possible_errors from their
        # parent into a new set
        custom_possible_errors = cls.__dict__.get("possible_errors", None)
        if custom_possible_errors is not None:
            del cls.possible_errors
            cls.possible_errors = custom_possible_errors | cls.possible_errors
        else:
            cls.possible_errors = set(cls.possible_errors)

        # Subclasses automatically generate a ChainMapping for their
        # 'responses' attribute
        custom_responses = cls.__dict__.get("responses")
        if custom_responses is not None:
            del cls.responses
        cls.responses = cls.responses.new_child(custom_responses)

    def __init__(self, node: "node.Node", method_name: str):

        super().__init__()

        self.__node = node
        self.__method_name = method_name
        self.parameters = list(self.parameters)
        self.responses = dict(
            (
                status,
                self._normalize_response_spec(spec, status)
            )
            for status, spec in self.responses.items()
        )

    def _normalize_response_spec(
            self,
            spec: Union[ResponseSpec, dict],
            status: int) -> ResponseSpec:

        if not isinstance(spec, ResponseSpec):
            spec = spec.copy()

            if not "content" in spec:
                response_type = (
                    self.response_type
                    or self.__node.response_type
                )
                if response_type:
                    spec.setdefault("type", response_type)

            try:
                spec = ResponseSpec(**spec)
            except ValueError:
                raise ResponseSpecError(self, spec)

        if not spec.description:
            spec.description = http.client.responses.get(status)

        return spec

    def __repr__(self):
        return f"{repr(self.__node)} {self.method_name}"

    @property
    def node(self) -> "node.Node":
        """The `Node` that the method belongs to."""
        return self.__node

    @property
    def parent(self) -> "node.Node":
        """Synonimous to the `node` property."""
        return self.__node

    @property
    def method_name(self) -> str:
        """The name of the implemented HTTP method."""
        return self.__method_name

    def handle_request(self):

        # Handle CORS
        if self.should_handle_cors():
            self.handle_cors()

        # Set the default MIME type for the response
        response_type = self.get_default_response_type()
        if response_type:
            cherrypy.response.headers["Content-Type"] = response_type

        # Assign arguments in the path
        args = getattr(cherrypy.request, "arguments", None)
        self.arguments = args if args else {}

        # Process query string parameters
        if self.parameters:

            # Collect values from the query string, applying the proper
            # deserialization procedure (see cocktail.controllers.parameters)
            self.values = {}

            for parameter in self.parameters:
                value = get_parameter(parameter, **self.parameter_options)
                if self.parameter_coercion is not Coercion.FAIL:
                    value = parameter.coerce(
                        value,
                        self.parameter_coercion,
                        **self.parameter_validation_options
                    )
                self.values[parameter.name] = value

            # If parameter coercion was set to FAIL, apply the delayed
            # validation now that all parameters have been collected
            if self.parameter_coercion is Coercion.FAIL:
                parameters_schema = Schema(
                    name =
                        get_full_name(self.__node.__class__)
                        + "."
                        + self.method_name,
                    members=self.parameters
                )
                parameters_schema.coerce(
                    self.values,
                    Coercion.FAIL,
                    **self.parameter_validation_options
                )

        # Process the request body
        if self.request_body:
            self.data = self.request_body.process()

        # Fire the 'responding' event
        self.responding()

        # Invoke the method's logic
        response_data = self.respond()

        # Automatically format responses (ie. JSON and YAML)
        if self.format_response:
            response_data = format_response(response_data)

        # Automatically encode unicode responses
        if self.response_encoding and isinstance(response_data, str):
            response_data = response_data.encode(self.response_encoding)

        return response_data

    def get_default_response_type(self) -> Optional[str]:
        """Obtains the default response type for the method."""
        for handler in self.ascend_handlers():
            if handler.response_type:
                return handler.response_type

    @request_property
    def arguments(self) -> Dict[str, Any]:
        """The values of dynamic path components for the current request."""
        return {}

    @request_property
    def values(self) -> Dict[str, Any]:
        """The values of query string / form parameters for the current
        request.
        """
        return {}

    @request_property
    def data(self) -> Any:
        """The values within the body submitted by the current request."""
        pass

    @abstractmethod
    def respond(self) -> Union[str, bytes, None]:
        """Implements the logic for the method."""
        pass

    def should_handle_cors(self) -> bool:
        """Determines if the method should resolve and produce CORS related
        headers for the current request.
        """
        return self.cors_enabled

    def handle_cors(self):
        """Resolves and produces CORS related headers for the current
        request.
        """
        h = cherrypy.response.headers
        origin = cherrypy.request.headers.get("Origin")
        allowed_origin = None

        if not origin:
            allowed_origins = self.resolve_allowed_origins()
            if allowed_origins is any_origin:
                allowed_origin = "*"
        elif self.allows_origin(origin):
            allowed_origin = origin

        if allowed_origin:
            h["Access-Control-Allow-Origin"] = allowed_origin
            if allowed_origin != "*":
                vary = h.get("Vary") or ""
                if vary:
                    h["Vary"] = f"{vary}, Origin"
                else:
                    h["Vary"] = "Origin"

        h["Access-Control-Allow-Methods"] = ", ".join(self.node.methods)
        h["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)


class ResponseSpecError(Exception):
    """An exception raised when declaring an invalid response for a `Method`."""

    def __init__(self, method: Method, spec: dict):
        super().__init__(
            f"Invalid response spec {spec} at {method}"
        )
        self.method = method
        self.spec = spec

