"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import (
    GenericMethod,
    SetWrapper,
    ListWrapper,
    DictWrapper
)
from datetime import datetime, date, time
from typing import (
    Dict,
    List,
    Union
)
from decimal import Decimal
from fractions import Fraction
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


@GenericMethod
def to_json_value(value):
    raise TypeError(f"Can't serialize {obj} to JSON")


@to_json_value.implementation_for(datetime)
def datetime_to_json_value(value):
    return value.isoformat()


@to_json_value.implementation_for(date)
def date_to_json_value(value):
    return value.isoformat()


@to_json_value.implementation_for(time)
def time_to_json_value(value):
    return value.isoformat()

@to_json_value.implementation_for(Decimal)
def decimal_to_json_value(value):
    return float(value)

@to_json_value.implementation_for(Fraction)
def fraction_to_json_value(value):
    return str(value)

@to_json_value.implementation_for(set)
@to_json_value.implementation_for(SetWrapper)
def set_to_json_value(value):
    return list(value)

@to_json_value.implementation_for(ListWrapper)
def list_wrapper_to_json_value(value):
    return value._items

@to_json_value.implementation_for(DictWrapper)
def dict_wrapper_to_json_value(value):
    return value._items


class ExtensibleJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        return to_json_value(obj)

