"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import (
    Dict,
    List,
    Union
)
from copy import deepcopy

import json

json_object = Dict[str, "json_data"]
json_list = List["json_data"]

json_data = Union[
    None,
    int,
    float,
    bool,
    str,
    json_object,
    json_list
]

json_template = Union[str, json_object]

def resolve_json_document(document: json_template) -> json_object:
    if isinstance(document, str):
        return json.loads(document)
    return document

def merge_json_documents(
        base: json_template,
        overlay: json_template) -> json_object:

    base = resolve_json_document(base)
    overlay = resolve_json_document(overlay)

    if base and overlay:
        return merge_json_data(base, overlay)
    elif base:
        return deepcopy(base)
    elif overlay:
        return deepcopy(overlay)

    return {}

def merge_json_data(
        base: json_object,
        overlay: json_object) -> json_object:

    merge = base.copy()

    for key, overlay_value in list(overlay.items()):
        if isinstance(overlay_value, dict):
            try:
                base_value = base[key]
            except KeyError:
                merge[key] = overlay_value.copy()
            else:
                merge[key] = merge_json_data(base_value, overlay_value)
        elif isinstance(overlay_value, list):
            merge[key] = deepcopy(overlay_value)
        else:
            merge[key] = overlay_value

    return merge

