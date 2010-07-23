#-*- coding: utf-8 -*-
u"""Utilities covering typical HTML design patterns.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from itertools import izip, cycle
from cocktail.html.element import get_current_renderer

def alternate_classes(element, classes = ("odd", "even")):
    
    @element.when_ready
    def alternate_classes_handler():
        children = (child for child in element.children if child.rendered)
        for child, cls in izip(children, cycle(classes)):
            child.add_class(cls)
    
def first_last_classes(element, first_class = "first", last_class = "last"):

    @element.when_ready
    def first_last_classes_handler():
        for child in element.children:
            if child.rendered:
                child.add_class(first_class)
                break
        else:
            return

        for child in reversed(element.children):
            if child.rendered:
                child.add_class(last_class)
                break

def html5_tag(element, tag):

    @element.when_ready
    def set_html5_alternative_tag():
        if getattr(get_current_renderer(), "html_version", None) >= 5:
            element.tag = tag

def html5_attr(element, key, value):

    @element.when_ready
    def set_html5_attribute():
        if getattr(get_current_renderer(), "html_version", None) >= 5:
            element[key] = value

_entity_expr = re.compile("[\"<>&]")
_entity_dict = {
    "\"": "&quot;",
    "<": "&lt;",
    ">": "&gt;",
    "&": "&amp;"
}
_entity_translation = lambda match: _entity_dict[match.group(0)]

def escape_attrib(value):
    return _entity_expr.sub(_entity_translation, value)

