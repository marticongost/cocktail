"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Iterable

from cocktail.pkgutils import import_object

_schemas = {}

def iter_schemas():
    return _schemas.values()

def register_schema(schema, full_name):
    _schemas[full_name] = schema

def get_schema(full_name):
    try:
        return _schemas[full_name]
    except KeyError:
        raise KeyError(f"No schema named {full_name}")

def import_type(full_name):

    schema = _schemas.get(full_name)
    if schema:
        return schema

    # Transform foobar.Spam into foobar.spam.Spam
    parts = full_name.split(".")
    if len(parts) < 2 or parts[-2] != parts[-1].lower():
        parts.insert(-1, parts[-1].lower())
        expanded_name = ".".join(parts)
        schema = _schemas.get(expanded_name)
        if schema:
            return schema

    return import_object(full_name)

