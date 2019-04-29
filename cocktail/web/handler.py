"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import (
    Any,
    Iterable,
    Mapping,
    Set,
    Union
)
from abc import ABCMeta, abstractmethod

import cherrypy

from cocktail.events import Event
from .errorresponses import (
    error_responses as default_error_responses,
    ErrorResponseMap,
    ErrorResponse
)


class AnyOrigin:

    def __contains__(self, origin):
        return True


any_origin = AnyOrigin()


class Inherit:
    pass


inherit = Inherit()


class Handler(metaclass=ABCMeta):
    """Base class for request handlers.

    This is an abstract class providing common functionality to
    `~cocktail.web.node.Node` and `~cocktail.web.method.Method`.
    """
    error_responses: ErrorResponseMap = default_error_responses
    allowed_origins: Union[Inherit, AnyOrigin, Set[str]] = inherit
    allowed_headers: Set[str] = {"Content-Type", "Authorization"}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Subclasses create their own Handler.error_responses, chained to the
        # one on its parent
        custom_responses = cls.__dict__.get("error_responses", None)
        if custom_responses is not None:
            del cls.error_responses
            cls.error_responses = cls.error_responses.new_child(
                custom_responses
            )
        else:
            cls.error_responses = cls.error_responses.new_child()

    before_request = Event(doc = """
        An event triggered before the handler (or one of its nested handlers)
        has been executed.
        """)

    after_request = Event(doc = """
        An event triggered after the controller (or one of its nested handlers)
        has been executed. This is guaranteed to run, regardless of errors.
        """)

    exception_raised = Event(doc = """
        An event triggered when an exception is raised by the handler or one
        of its descendants.

        The event is propagated up through the handler chain, until it reaches
        the top or it is stoped by setting its `handled` attribute to True.

        .. attribute:: exception

            The exception being reported.

        .. attribute:: handled

            A boolean indicating if the exception has been dealt with. Setting
            this to True will stop the propagation of the event up the handler
            chain, while a False value will cause the exception to continue to
            be bubbled up towards the application root and, eventually, the
            user.
        """)

    def ascend_handlers(self) -> Iterable["Handler"]:
        """Produces the iterable sequence of `Handler` objects for this handler
        and its ancestors.

        The method yields the handler itself first, and iterates upwards
        towards the root handler, which is returned in last place.
        """
        handler = self
        while handler:
            yield handler
            handler = handler.parent

    def iter_handlers_from_root(self) -> Iterable["Handler"]:
        """Produces the iterable sequence of `Handler` objects for this handler
        and its ancestors, starting from the root.

        The method yields the root handler first, and iterates inwards towards
        the handler itself, which is returned in last place.
        """
        parent = self.parent
        if parent:
            yield from parent.iter_handlers_from_root()
        yield self

    @property
    @abstractmethod
    def parent(self) -> "Handler":
        """Returns the parent handler for this handler."""
        pass

    def allows_origin(self, origin: str) -> bool:
        """Determine if the given origin is acceptable."""
        return origin in self.resolve_allowed_origins()

    def resolve_allowed_origins(self) -> Union[AnyOrigin, Set[str]]:
        """Resolves the value of the `allowed_origins` property, recursing to
        parent handlers when the value is set to `inherit`.

        If the root of the handler tree is reached and the value is still
        `inherit`, the method returns an empty set.
        """
        if self.allowed_origins is inherit:
            parent = self.parent
            return (
                parent and parent.resolve_allowed_origins()
                or set()
            )

        return self.allowed_origins

    def __call__(self) -> Any:
        """Handle the current request, producing the appropiate response."""

        handlers = list(self.ascend_handlers())

        try:
            for handler in reversed(handlers):
                handler.before_request()

            return self.handle_request()

        except Exception as error:

            # Redirections skip error handling
            if (
                isinstance(error, cherrypy.HTTPError)
                and error.status >= 300 <= 400
            ):
                raise

            return self.handle_error(error)

        finally:
            for handler in handlers:
                self.after_request()

    @cherrypy.expose
    def index(self, **kwargs):
        return self()

    @abstractmethod
    def handle_request(self):
        pass

    def handle_error(self, error: Exception) -> ErrorResponse:
        """Handle an exception raised during the invocation of this handler or
        one of its nested handlers.
        """
        # Fire an event on the handler and each of its ancestors
        for handler in self.ascend_handlers():
            handler.exception_raised(error=error)

        # Find a suitable response for the exception
        error_response = self.get_error_response(error)
        return error_response.respond(error)

    def get_error_response(self, error: Exception) -> ErrorResponse:
        """Gets the error response that should handle the given exception."""
        for handler in self.ascend_handlers():
            error_response = self.error_responses.get(error.__class__)
            if error_response is not None:
                return error_response

        return None

    def apply_error_response(
            self,
            error: Exception,
            error_response: ErrorResponse) -> Any:
        """Applies the given response to an exception."""
        error_response.applying(error=error)
        cherrypy.response.status = error_response.status


