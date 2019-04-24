"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Type,
    Union
)

import cherrypy

from cocktail.events import Event
from cocktail.yamlutils import yaml_template
from cocktail.controllers import get_parameter
from cocktail import schema
from .errorresponses import error_response
from .handler import Handler
from .method import Method


class Node(Handler):
    """Base class for nodes in a RESTful API."""

    arguments: Sequence[Dict] = ()
    children: Mapping[str, Type["Node"]] = {}
    wildcards: Sequence[Type["Node"]] = []
    response_type: str = None
    private: bool = False
    open_api: yaml_template = None

    traversed = Event(doc = """
        An event triggered when the CherryPy dispatcher passes through or
        reaches this node while dispatching a request.

        .. attribute:: path

            A list-like object containing the remaining path components
            that haven't been consumed by the dispatcher yet.
        """)

    def __init__(self):
        super().__init__()
        self.__name = None
        self.__parent = None
        self.__children = {}
        self.__wildcards = []
        self.__methods = {}

        # Instantiate child nodes
        for name, node_cls in self.children.items():
            self.add(node_cls(), name)

        # Instantiate wildcard nodes
        for node_cls in self.wildcards:
            self.add(node_cls())

        # Instantiate methods
        for key in dir(self):
            value = getattr(self, key, None)
            if isinstance(value, type) and issubclass(value, Method):
                assert key == key.upper(), \
                    "HTTP methods must be all in uppercase"
                method = self.create_method(value, key)
                self.__methods[key] = method

    def __repr__(self):
        return f"{self.__class__.__name__} {self.get_path()}"

    def get_path(self, arguments: Mapping[str, Any] = None) -> str:
        """Gets the string path for the node"""
        return "/" + "/".join(self.get_path_components(arguments))

    def get_path_components(
            self,
            arguments: Mapping[str, Any] = None) -> List[str]:
        """Gets a list containing the distinct components of the node's
        path.
        """
        if self.__parent:
            components = self.__parent.get_path_components()
        else:
            components = []

        if self.__name:
            components.append(self.__name)

        if self.arguments:
            for arg in self.arguments:

                if arguments:
                    try:
                        value = arguments[arg.name]
                    except KeyError:
                        if arg.required:
                            raise
                        else:
                            pass
                    else:
                        if arg.serialize_request_value:
                            value = arg.serialize_request_value(value)

                        components.append(value)

                elif arg.required:
                    components.append("{%s}" % arg.name)

        return components

    @property
    def children(self) -> Dict[str, "Node"]:
        """The child nodes of this node."""
        return self.__children

    @property
    def wildcards(self) -> List["Node"]:
        """The list of wildcard nodes (anonymous, argument based nodes) of this
        node.
        """
        return self.__wildcards

    def add(self, node: "Node", name: str = None):
        """Add a nested node."""

        if node.__parent:
            raise NodeRelocationError(node, node.__parent, self, name)

        node.__parent = self

        if name:
            node.__name = name
            self.__children[node.__name] = node
        else:
            self.__wildcards.append(node)

    @property
    def name(self) -> Optional[str]:
        """The name of the node."""
        return self.__name

    @property
    def parent(self) -> Optional["Node"]:
        """The parent node that contains the node."""
        return self.__parent

    def iter_nodes(
            self,
            include_self: bool = False,
            recursive: bool = False) -> Iterable["Node"]:
        """Iterates over the node contained within the node."""

        if include_self:
            yield self

        if recursive:
            for child in self.__children.values():
                yield from child.iter_nodes(
                    include_self=True,
                    recursive=True
                )

            for wildcard in self.__wildcards:
                yield from wildcard.iter_nodes(
                    include_self=True,
                    recursive=True
                )
        else:
            yield from self.__children.values()

    @property
    def methods(self) -> Dict[str, "Method"]:
        """The methods implemented by this node."""
        return self.__methods

    def create_method(
            self,
            method_class: Type[Method],
            method_name: str) -> Method:
        """Creates the implementation of a given HTTP method for this node.

        This method allows nodes to apply common initialization to their
        methods.
        """
        return method_class(self, method_name)

    def _cp_dispatch(self, vpath):

        # Override the default CherryPy dispatching algorithm

        self.traversed(path = vpath)

        if vpath:
            child = self.__children.get(vpath[0])
            if child:
                vpath.pop(0)
                return child

        if (
            self.arguments
            and getattr(cherrypy.request, "wildcard", None) is not self
            and not self.process_arguments(vpath)
        ):
            return None

        if vpath:
            for wildcard in self.__wildcards:
                if wildcard.process_arguments(vpath):
                    cherrypy.request.wildcard = wildcard
                    return wildcard

            return None

        return self

    def process_arguments(
            self,
            path: Sequence[str]) -> Optional[Dict[str, Any]]:
        """Extract the positional arguments for the node for the current
        request.

        If the path for the current request doesn't match the expected
        arguments (either not enough path components are supplied, or one of
        the extracted values doesn't pass validation) the method will leave
        `path` untouched and return 'None'.

        If all expected values can be correctly extracted and validated, the
        resulting values are merged into the 'cherrypy.request.arguments'
        mapping, along with any preceding arguments previously loaded by an
        ancestor node. The method will pop all extracted values from `path`
        (to indicate the matching path components have been consumed), and
        return a mapping with the values extracted by this node.
        """
        arg_values = {}

        for n, arg in enumerate(self.arguments):
            try:
                raw_value = path[n]
            except IndexError:
                raw_value = None

            value = get_parameter(
                arg,
                source=(lambda key: raw_value),
                errors="ignore",
                undefined="set_default",
                implicit_booleans=False
            )

            if not arg.validate(value):
                return None

            arg_values[arg.name] = value

        for v in arg_values:
            path.pop(0)

        # Store values in cherrypy.request.arguments
        try:
            request_arguments = cherrypy.request.arguments
        except AttributeError:
            cherrypy.request.arguments = arg_values
        else:
            request_arguments.update(arg_values)

        return arg_values

    def handle_request(self):
        try:
            method = self.__methods[cherrypy.request.method]
        except KeyError:
            raise cherrypy.HTTPError(405, "Not Implemented") from None

        return method()

    class OPTIONS(Method):
        """Default response for CORS pre-flight requests.

        See `cocktail.web.Handler.handle_cors` for the actual implementation of
        CORS headers.
        """

        responses = {
            204: {}
        }

        def respond(self):
            cherrypy.response.status = 204


class NodeRelocationError(Exception):
    """An exception raised when attempting to relocate a `Node` to a new
    position in the API tree.
    """
    node: Node
    current_parent: Node
    current_name: str
    new_parent: Node
    new_name: str

    def __init__(
        self,
        node: Node,
        current_parent: Node,
        current_name: str,
        new_parent: Node,
        new_name: str
    ):
        super().__init__(
            f"Can't relocate node {node} "
            f"from {current_parent} '{current_name}' "
            f"to {new_parent} '{new_name}'"
        )
        self.node = node
        self.current_parent = old_parent
        self.current_name = old_name
        self.new_parent = new_parent
        self.new_name = new_name


class InvalidInputError(Exception):
    """An exception raised when a method receives invalid parameters in its
    query string or request body.
    """

    def __init__(self, node, errors: schema.ErrorList = None):
        super().__init__(self, f"Invalid parameters for {node}")

