"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Union
from copy import deepcopy

import yaml

from .jsonutils import json_object, merge_json_data

yaml_template = Union[str, json_object]

def resolve_yaml_document(document: yaml_template) -> json_object:
    if isinstance(document, str):
        return yaml.load(document)
    return document

def merge_yaml_documents(
        base: yaml_template,
        overlay: yaml_template) -> json_object:

    base = resolve_yaml_document(base)
    overlay = resolve_yaml_document(overlay)

    if base and overlay:
        return merge_json_data(base, overlay)
    elif base:
        return deepcopy(base)
    elif overlay:
        return deepcopy(overlay)

    return {}

