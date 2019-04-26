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
import collections
import http.client
import sys

import yaml
import cherrypy
import requests

from cocktail.jsonutils import json_object
from cocktail.yamlutils import (
    yaml_template,
    resolve_yaml_document,
    merge_yaml_documents,
    merge_json_data
)
from cocktail import schema
from cocktail.controllers import get_request_root_url
from .node import Node
from .method import Method
from .requestbody import RequestBody, MultipleRequestBodies
from .responsespec import ResponseSpec
from .errorresponses import ErrorResponse, structured_content_types

JSON_MIME = "application/json"
YAML_MIME = "application/x-yaml"
SWAGGERHUB_ENDPOINT = "https://api.swaggerhub.com/apis/{owner}/{api}"

class Default:
    pass

default = Default()


class OpenAPIGenerator:

    template: Union[dict, str] = {
        "openapi": "3.0.0",
        "info": {
            "version": "1.0.0"
        }
    }

    custom_template: yaml_template = None
    schema_components: Dict[str, schema.Member] = {}
    parameter_components: Dict[str, schema.Member] = {}
    request_body_components: Dict[str, RequestBody] = {}
    response_components: Dict[str, ResponseSpec] = {}

    def __init__(
        self,
        custom_template:
            Union[Default, None, yaml_template] = default,
        schema_components:
            Union[Default, Dict[str, schema.Member]] = default,
        parameter_components:
            Union[Default, Dict[str, schema.Member]] = default,
        request_body_components:
            Union[Default, Dict[str, RequestBody]] = default,
        response_components:
            Union[Default, Dict[str, ResponseSpec]] = default
    ):
        if custom_template is not default:
            self.custom_template = custom_template

        if schema_components is default:
            schema_components = self.schema_components

        if parameter_components is default:
            parameter_components = self.parameter_components

        if request_body_components is default:
            request_body_components = self.request_body_components

        if response_components is default:
            response_components = self.response_components

        self.schema_components = schema_components.copy()
        self.parameter_components = parameter_components.copy()
        self.request_body_components = request_body_components.copy()
        self.response_components = response_components.copy()

        self.__component_index = {}
        self._index_components("schemas", schema_components)
        self._index_components("parameters", parameter_components)
        self._index_components("requestBodies", request_body_components)
        self._index_components("responses", response_components)

    def _index_components(self, component_type, mapping):
        if mapping:
            for name, element in mapping.items():
                self.__component_index[component_type, element] = name

    def get_servers(self) -> Optional[List[dict]]:
        return [
            {"url": str(get_request_root_url())}
        ]

    def create_base_document(self):
        return merge_yaml_documents(self.template, self.custom_template)

    def create_document(self, root_node: Node) -> json_object:

        document = self.create_base_document()

        servers = self.get_servers()
        if servers is not None:
            servers_list = document.get("servers")
            if servers_list is None:
                document["servers"] = servers_list = []
            servers_list.extend(servers)

        components_info = document.get("components")
        if components_info is None and (
            self.schema_components
            or self.parameter_components
            or self.request_body_components
            or self.response_components
        ):
            document["components"] = components_info = {}

        # Schema components
        # Explicit schema components plus automatically generated error schemas
        schema_components_info = {}

        if self.schema_components:
            for name, schema in self.schema_components.items():
                schema_components_info[name] = self.export_schema(
                    schema,
                    allow_refs=False
                )

        for node in self.iter_nodes(root_node):
            for method_name, method in node.methods.items():
                if self.should_include_method(method):
                    for error_type in self.get_possible_errors(method):
                        error_response = method.error_responses.get(error_type)
                        if error_response:
                            error_schema_name = self.get_name_of_error_schema(
                                error_response,
                                error_type
                            )
                            if error_schema_name not in schema_components_info:
                                schema_components_info[error_schema_name] = \
                                    self.export_error_schema(
                                        error_response,
                                        error_type
                                    )

        if schema_components_info:
            components_info["schemas"] = schema_components_info

        # Parameter components
        if self.parameter_components:
            components_info["parameters"] = params_info = {}
            for name, parameter in self.parameter_components.items():
                params_info[name] = self.export_parameter(
                    parameter,
                    allow_refs=False
                )

        # Request body components
        if self.request_body_components:
            components_info["requestBodies"] = bodies_info = {}
            for name, body in self.request_body_components.items():
                bodies_info[name] = self.export_body(
                    body,
                    allow_refs=False
                )

        # Response components
        if self.response_components:
            components_info["responses"] = params_info = {}
            for name, response in self.response_components.items():
                params_info[name] = self.export_response(
                    response,
                    allow_refs=False
                )

        # Paths
        paths_map = {}
        document["paths"] = paths_map

        for node in self.iter_nodes(root_node):

            methods = [
                (method_name, method)
                for method_name, method in node.methods.items()
                if self.should_include_method(method)
            ]

            if not methods:
                continue

            node_info = {}

            # Path parameters
            arg_list = []
            for ancestor in reversed(list(node.ascend_handlers())):
                for arg in ancestor.arguments:
                    arg_list.append(self.export_argument(arg))

            if arg_list:
                node_info["parameters"] = arg_list

            # Methods
            for method_name, method in methods:

                summary = self.get_summary(method)
                description = self.get_description(method)
                tags = self.get_tags(method)
                operation_id = self.get_operation_id(method)
                method_info = {}

                if summary:
                    method_info["summary"] = summary

                if description:
                    method_info["description"] = description

                if tags:
                    method_info["tags"] = tags

                if operation_id:
                    method_info["operationId"] = operation_id

                # Query parameters
                if method.parameters:
                    method_info["parameters"] = param_list = []
                    for parameter in method.parameters:
                        param_list.append(
                            self.export_parameter(parameter, "query")
                        )

                # Request bodies
                if method.request_body:
                    method_info["requestBody"] = body_info = \
                        self.export_body(method.request_body)

                # Method responses
                # Group error responses by status, aggregate their possible
                # errors. Sample:
                # {200: {AuthErrorResponse: {LoginError, PermissionError}}}
                response_codes = set(method.responses)
                error_responses = collections.defaultdict(
                    lambda: collections.defaultdict(set)
                )
                for error_type in self.get_possible_errors(method):
                    error_response = method.error_responses.get(error_type)
                    if error_response:
                        for status in error_response.iter_status_codes():
                            response_codes.add(status)
                            error_responses[status][error_response].add(error_type)

                response_type = method.get_default_response_type()
                method_info["responses"] = response_map = dict(
                    (
                        status,
                        self.export_response(
                            method.responses.get(status)
                                or ResponseSpec(
                                    type=response_type,
                                    description=http.client.responses.get(status)
                                ),
                            error_responses=error_responses.get(status)
                        )
                    )
                    for status in response_codes
                )

                # Custom template for methods
                if method.open_api:
                    method_info = merge_json_data(
                        method_info,
                        resolve_yaml_document(method.open_api)
                    )

                node_info[method_name.lower()] = method_info

            # Custom template for nodes
            if node.open_api:
                node_info = merge_json_data(
                    node_info,
                    resolve_yaml_document(node.open_api)
                )

            if node_info:
                paths_map[node.get_path()] = node_info

        return document

    def iter_nodes(self, root: Node) -> Iterable[Node]:
        for node in root.iter_nodes(recursive=True):
            if self.should_include_node(node):
                yield node

    def should_include_node(self, node: Node) -> bool:
        return not node.private

    def should_include_method(self, method: Method) -> bool:
        return method.method_name != "OPTIONS"

    def get_component_ref(self, component_type, obj):
        key = self.__component_index.get((component_type, obj))
        if key:
            return {"$ref": f"#/components/{component_type}/{key}"}
        else:
            return None

    def export_body(
        self,
        request_body: RequestBody,
        allow_refs: bool = True) -> json_object:

        if allow_refs:
            ref = self.get_component_ref("request_bodies", request_body)
            if ref:
                return ref

        data = {}

        if request_body.required:
            data["required"] = True

        data["content"] = content_info = {}

        for body in request_body.iter_bodies():
            for type in body.types:
                content_info[type] = type_info = {}
                if body.schema:
                    type_info["schema"] = self.export_schema(body.schema)

        return data

    def get_possible_errors(self, method):

        errors = set(method.possible_errors)

        if (
            method.parameter_coercion in (
                schema.Coercion.FAIL,
                schema.Coercion.FAIL_IMMEDIATELY
            )
            or (
                method.request_body and method.request_body.coercion in (
                    schema.Coercion.FAIL,
                    schema.Coercion.FAIL_IMMEDIATELY
                )
            )
        ):
            errors.add(schema.exceptions.InputError)

        return errors

    def get_name_of_error_schema(
            self,
            error_response: ErrorResponse,
            error_type: Type[Exception]) -> str:

        return error_type.__name__

    def export_error_schema(
            self,
            error_response: ErrorResponse,
            error_type: Type[Exception]) -> json_object:

        error_schema = error_response.error_schema

        if error_schema is None:
            info = {"properties": {}}
        else:
            info = self.export_schema(error_schema)

        if not info.get("description"):
            info["description"] = self.get_description(error_type)

        info["properties"]["type"] = {
            "type": "string",
            "enum": [error_type.__name__],
            "description": "A code indicating the type of error"
        }

        info["properties"]["message"] = {
            "type": "string",
            "description": "A user readable description of the error"
        }

        return info

    def export_schema(
            self,
            member: Union[schema.Member, Sequence[schema.Member]],
            dest: json_object = None,
            allow_refs: bool = True) -> json_object:

        if dest is None:
            dest = {}

        # Describe multiple schema choices using oneOf
        if (
            isinstance(member, collections.Sized)
            and isinstance(member, collections.Iterable)
        ):
            dest["oneOf"] = [
                self.export_schema(option)
                for option in member
            ]
            return dest

        if not isinstance(member, schema.Member):
            raise ValueError(
                "Expected a schema.Member object or a sequence of "
                f"schema.Member objects; got {member} instead."
            )

        if allow_refs:
            ref = self.get_component_ref("schemas", member)
            if ref:
                return ref
            elif isinstance(member, schema.Record) and member.record_schema:
                ref = self.get_component_ref("schemas", member.record_schema)
                if ref:
                    return ref

        if isinstance(member, schema.Integer):
            dest["type"] = "integer"
        elif isinstance(member, (schema.Float, schema.Decimal)):
            dest["type"] = "number"
        elif isinstance(member, schema.Boolean):
            dest["type"] = "boolean"
        elif isinstance(member, schema.EmailAddress):
            dest["type"] = "string"
            dest["format"] = "email"
        elif isinstance(member, schema.String):
            dest["type"] = "string"
        elif isinstance(member, schema.Time):
            dest["type"] = "string"
            dest["format"] = "time"
        elif isinstance(member, schema.DateTime):
            dest["type"] = "string"
            dest["format"] = "date-time"
        elif isinstance(member, schema.Date):
            dest["type"] = "string"
            dest["format"] = "date"
        elif isinstance(member, schema.Enumeration):
            dest["type"] = "string"
            if member.type:
                dest["enum"] = list(member.type.__members__)
        elif isinstance(member, schema.Mapping):
            dest["type"] = "object"

            if member.keys:
                names = self.export_schema(member.keys)
                names.pop("type", None)
                if names:
                    dest["propertyNames"] = names

            if member.values:
                dest["additionalProperties"] = self.export_schema(member.values)

        elif isinstance(member, schema.Collection):
            dest["type"] = "array"
            if member.items:
                dest["items"] = self.export_schema(member.items)
        elif isinstance(member, schema.Reference):
            if member.related_type:
                primary_key = member.related_type.primary_member
                if primary_key:
                    self.export_schema(primary_key, dest=dest)
        elif isinstance(member, (schema.Record, schema.Schema)):

            source_schema = (
                member.record_schema
                    if isinstance(member, schema.Record)
                    else member
            )

            if source_schema:
                dest["type"] = "object"
                dest["properties"] = props_info = {}

                required_fields = []
                for field in source_schema.iter_members():
                    props_info[field.name] = self.export_schema(field)
                    if field.required:
                        required_fields.append(field.name)

                if required_fields:
                    dest["required"] = required_fields

        if isinstance(member, schema.RangedMember):
            if member.min is not None:
                dest["minimum"] = member.to_json_value(member.min)
            if member.max is not None:
                dest["maximum"] = member.to_json_value(member.max)

        if member.default is not None:
            dest["default"] = member.to_json_value(member.default)

        if member.enumeration:
            dest["enum"] = [
                member.to_json_value(item)
                for item in member.enumeration
            ]

        description = self.get_description(member)
        if description:
            dest["description"] = description

        example = self.get_member_example(member)
        if example is not None:
            dest["example"] = member.to_json_value(example)

        return dest

    def export_parameter(
            self,
            member: schema.Member,
            location: str = "query",
            allow_refs: bool = True) -> json_object:

        if allow_refs:
            ref = self.get_component_ref("parameters", member)
            if ref:
                return ref

        data = {
            "name": member.name,
            "in": location
        }

        description = self.get_description(member)
        if description:
            data["description"] = description

        data["schema"] = self.export_schema(member)

        if self.parameter_is_required(member):
            data["required"] = member.required

        return data

    def parameter_is_required(self, member: schema.Member) -> bool:
        return member.required and member.default is None

    def export_argument(self, arg: schema.Member) -> json_object:
        return self.export_parameter(arg, location="path")

    def export_header(self, header: schema.Member) -> json_object:
        data = {
            "schema": self.export_schema(header)
        }
        description = self.get_description(header)
        if description:
            data["description"] = description
        return data

    def export_response(
            self,
            response: ResponseSpec,
            error_responses:
                Mapping[ErrorResponse, Set[Type[Exception]]] = None,
            allow_refs: bool = True) -> json_object:

        if allow_refs:
            ref = self.get_component_ref("responses", response)
            if ref:
                return ref

        data = {}

        description = response.description
        if description:
            data["description"] = self.process_text(description)

        if response.headers:
            data["headers"] = dict(
                (header.name, self.export_header(header))
                for header in response.headers
            )

        if response.content:
            data["content"] = content_info = {}

            for type, type_spec in response.content.items():
                content_info[type] = type_info = {}
                error_schema_info = None
                type_schema_info = None
                type_schema = type_spec.get("schema")

                if type_schema:
                    type_schema_info = self.export_schema(type_schema)

                if type in structured_content_types and error_responses:
                    error_schema_refs = []
                    for error_response, error_types in error_responses.items():
                        for error_type in error_types:
                            error_schema_name = self.get_name_of_error_schema(
                                error_response,
                                error_type
                            )
                            error_schema_refs.append({
                                "$ref": "#/components/schemas/"
                                        + error_schema_name
                            })

                    if len(error_schema_refs) == 1:
                        error_schema_info = {
                            "type": "object",
                            "properties": {
                                "error": error_schema_refs[0]
                            },
                            "required": ["error"]
                        }
                    elif error_schema_refs:
                        error_schema_info = {
                            "type": "object",
                            "properties": {
                                "error": {
                                    "oneOf": error_schema_refs,
                                    "discriminator": {
                                        "propertyName": "type"
                                    }
                                }
                            },
                            "required": ["error"]
                        }

                if type_schema_info and error_schema_info:
                    merged_schema_info = {
                        "oneOf": [type_schema_info, error_schema_info]
                    }
                else:
                    merged_schema_info = type_schema_info or error_schema_info

                if merged_schema_info:
                    type_info["schema"] = merged_schema_info

        return data

    def get_summary(self, obj: Any) -> str:

        desc = (
            getattr(obj, "openapi_desc", None)
            or getattr(obj, "__doc__", "")
        )

        if not desc:
            return ""

        pos = desc.find(".")
        if pos != -1:
            desc = desc[:pos + 1]

        lines = []

        for line in desc.expandtabs().splitlines():
            line = line.strip()
            if line:
                lines.append(line)
            else:
                break

        return " ".join(lines)

    def get_description(self, obj: Any) -> str:

        desc = (
            getattr(obj, "openapi_desc", None)
            or getattr(obj, "__doc__", "")
        )

        if not desc:
            return ""

        return self.process_text(desc)

    def process_text(self, text):

        # Convert tabs to spaces (following the normal Python rules)
        # and split into a list of lines:
        lines = text.expandtabs().splitlines()

        # Determine minimum indentation (first line doesn't count):
        indent = sys.maxsize
        for line in lines[1:]:
            stripped = line.lstrip()
            if stripped:
                indent = min(indent, len(line) - len(stripped))

        # Remove indentation (first line is special):
        trimmed = [lines[0].strip()]
        if indent < sys.maxsize:
            for line in lines[1:]:
                trimmed.append(line[indent:].rstrip())

        # Strip off trailing and leading blank lines:
        while trimmed and not trimmed[-1]:
            trimmed.pop()
        while trimmed and not trimmed[0]:
            trimmed.pop(0)

        return " ".join(trimmed)

    def get_member_example(self, member):
        return getattr(member, "example", None)

    def get_operation_id(self, method):
        return getattr(method, "operation_id", None)

    def get_tags(self, method):
        return getattr(method, "tags", None)

    def join_descriptions(self, descriptions: Iterable[Optional[str]]) -> str:
        return "; ".join(descr for descr in descriptions if descr)

    def publish_to_swaggerhub(
            self,
            owner: str,
            api_name: str,
            api_spec: [Node, Type[Node], str, json_object],
            swaggerhub_key: str):

        # Normalize to a YAML string
        if isinstance(api_spec, str):
            data = api_spec
        elif isinstance(api_spec, type) and issubclass(api_spec, Node):
            data = yaml.dump(self.create_document(api_spec()))
        elif isinstance(api_spec, Node):
            data = yaml.dump(self.create_document(api_spec))
        else:
            data = yaml.dump(api_spec)

        response = requests.post(
            SWAGGERHUB_ENDPOINT.format(owner=owner, api=api_name),
            data=data,
            headers={
                "Content-Type": "application/yaml",
                "Authorization": swaggerhub_key
            }
        )
        response.raise_for_status()


class OpenAPINode(Node):
    """A node that exports the API of its parent as an Open API 3.0 document.
    """

    private = True

    arguments = [
        schema.String(
            name="format",
            enumeration=["json", "yaml"],
            required=True
        )
    ]

    generator: Type[OpenAPIGenerator] = OpenAPIGenerator
    generator_options: dict = {}

    class GET(Method):

        def respond(self):

            # Set the response type
            format = self.arguments["format"]
            if format == "json":
                mime = JSON_MIME
            else:
                mime = YAML_MIME

            cherrypy.response.headers["Content-Type"] = mime
            generator = self.node.generator(**self.node.generator_options)
            api_root = self.get_api_root()
            return generator.create_document(api_root)

        def get_api_root(self) -> Node:
            """Obtains the root of the API to document."""
            return self.node.parent

