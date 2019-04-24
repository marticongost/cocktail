"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    Sequence,
    Set,
    Type,
    Union
)
import traceback

import cherrypy

from cocktail.translations import translations
from cocktail.jsonutils import json_object
from cocktail.typemapping import ChainTypeMapping
from cocktail import schema
from cocktail.controllers.displayerror import format_error
from .responseformats import format_response

ErrorDataProducer = Callable[[Exception], json_object]
StatusDefinition = Union[int, Set[int]]

structured_content_types = {
    "application/json",
    "application/yaml",
    "application/x-yaml"
}

ErrorResponseMap = Mapping[Type[Exception], 'ErrorResponse']

error_responses: ErrorResponseMap = ChainTypeMapping()

ErrorResponseDecorator = Callable[[Type['ErrorResponse']], Type['ErrorResponse']]


def handles_error(
        *error_types: Type[Exception]) -> ErrorResponseDecorator:
    """
    A decorator that simplifies the mapping of exceptions to custom response
    classes.
    """
    def decorator(cls: Type['ErrorResponse']) -> Type['ErrorResponse']:
        instance = cls()
        for error_type in error_types:
            error_responses[error_type] = instance
        return cls

    return decorator


@handles_error(Exception)
class ErrorResponse:
    """A class that determines how a specific error type should be handled."""

    status: StatusDefinition = 500
    error_schema: schema.Schema = None
    print_tracebacks: bool = True

    def __init__(
        self,
        status: StatusDefinition = None,
        error_schema: schema.Schema = None
    ):
        if status is not None:
            self.status = status

        if error_schema is not None:
            self.error_schema = error_schema

    def respond(self, error: Exception) -> Any:
        """Respond to the given exception."""
        response_type = cherrypy.response.headers["Content-Type"]
        response_type = response_type.split(";", 1)[0]
        cherrypy.response.status = status = self.get_status(error)

        if self.should_print_traceback(error, status):
            traceback.print_exception(
                error.__class__,
                error,
                error.__traceback__
            )

        return self.get_content(error, response_type)

    def should_print_traceback(self, error: Exception, status: int) -> bool:
        """Deterimes if the given error should display an exception in the
        server log.
        """
        return 500 <= status < 600

    def get_status(self, error: Exception) -> int:
        """Obtains the HTTP status code for the given exception."""
        if isinstance(self.status, int):
            return self.status
        else:
            raise TypeError(
                "{self} can't determine the HTTP status code it should return "
                "for {error}; error responses with multiple possible status codes should "
                "reimplement their get_status() method"
            )

    def iter_status_codes(self) -> Iterable[int]:
        """Iterates over all the HTTP status codes that might be returned by
        this error response.
        """
        if isinstance(self.status, int):
            yield self.status
        else:
            yield from self.status

    def get_content(self, error: Exception, content_type: str) -> Any:
        """Obtains the response body for the given exception."""
        if content_type in structured_content_types:
            return format_response({"error": self.get_data(error)}, content_type)
        else:
            return format_error(error)

    def get_data(self, error: Exception) -> json_object:
        """Obtains the structured data for the given exception."""
        return {
            "type": error.__class__.__name__,
            "message": translations(error)
        }


@handles_error(cherrypy.HTTPError)
class HTTPErrorResponse(ErrorResponse):
    """Response type for explicitly raised `cherrypy.HTTPError` exceptions."""

    def get_status(self, error: Exception) -> int:
        return error.status


@handles_error(schema.exceptions.ValidationError)
class ValidationErrorResponse(ErrorResponse):
    """Response type for schema validation errors."""

    status = 400

    error_schema = schema.Schema(
        members={
            "type": schema.String(
                required=True,
                doc="An identifier for the validation rule that failed"
            ),
            "message": schema.String(
                required=True,
                doc="A human readable description of the validation error"
            ),
            "members": schema.Collection(
                items=schema.String(
                    required=True,
                    doc="The name of a member of the validated schema"
                ),
                doc="The members involved in the validation error"
            )
        }
    )

    def get_data(self, error: Exception) -> json_object:
        data = super().get_data(error)
        data["members"] = [
            member.name
            for member in error.invalid_members
            if member.name
        ]
        return data


@handles_error(schema.exceptions.InputError)
class InputErrorResponse(ErrorResponse):
    """Response type for schema coercion errors."""

    status = 400

    error_schema = schema.Schema(
        members={
            "errors": schema.Collection(
                items = schema.Record(
                    record_schema=ValidationErrorResponse.error_schema
                )
            )
        }
    )

    def get_data(self, error: Exception) -> json_object:
        data = super().get_data(error)
        val_error_resp = error_responses[schema.exceptions.ValidationError]
        data["errors"] = [
            val_error_resp.get_data(val_error)
            for val_error in error.errors
        ]
        return data

ExceptionTypeDecorator = Callable[[Type[Exception]], Type[Exception]]


def error_response(status: int) -> ExceptionTypeDecorator:
    """
    A decorator that simplifies the definition of error responses.
    """
    def decorator(cls: Type[Exception]) -> Type[Exception]:

        class CustomErrorResponse(ErrorResponse):
            pass

        CustomErrorResponse.__name__ = cls.__name__ + "Response"
        CustomErrorResponse.status = status
        error_responses[cls] = CustomErrorResponse()
        return cls

    return decorator

