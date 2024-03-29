"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Dict, List, Optional, Union, Sequence, Mapping

from cocktail.schema import Member, Schema


class Default:
    pass

default = Default()

media_content = Dict[str, dict]


class ResponseSpec:
    """A specification for one of the possible return values of an HTTP
    method.
    """
    content: media_content = {}
    description: str = None
    headers: List[Member] = []

    def __init__(
        self,
        type: Union[int, Default] = default,
        schema: Union[Member, Default] = default,
        content: Union[media_content, Default] = default,
        description: Union[str, Default] = default,
        headers: Union[List[Member], Default] = default
    ):
        self.content = self.content.copy()

        if content is not default:
            self.content.update(content)

        # Normalize member lists / mappings to a Schema object
        if isinstance(schema, (Sequence, Mapping)):
            schema = Schema(members=schema)

        if type is not default:
            self.content.update({
                type: {
                    "schema": None if schema is default else schema
                }
            })

        if schema is not default and type is default:
            raise ValueError(
                "Can't specify 'schema' without supplying a default response "
                "type"
            )

        if description is not default:
            self.description = description

        if headers is default:
            self.headers = list(self.headers)
        else:
            self.headers = list(headers)

    def resolve_response_type(
            self, type: str, subtype: str, **kwargs) -> Optional[str]:
        """Determines if the response matches the given response type."""

        requested_mime_type = f"{type}/{subtype}"

        if type == "*":
            return requested_mime_type

        if subtype == "*":
            prefix = type + "/"
            for mime_type in self.content:
                if mime_type.startswith(prefix):
                    return requested_mime_type

        if requested_mime_type in self.content:
            return requested_mime_type

        return None

