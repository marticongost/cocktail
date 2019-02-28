#-*- coding: utf-8 -*-
"""Utilities covering typical HTML design patterns.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from itertools import cycle
from decimal import Decimal
import bs4
from cocktail.events import when
from cocktail.urls import URL
from cocktail.html.rendering import get_current_rendering

def alternate_classes(element, classes = ("odd", "even")):

    @when(element.ready_stage)
    def alternate_classes_handler(e):
        children = (child for child in element.children if child.rendered)
        for child, cls in zip(children, cycle(classes)):
            child.add_class(cls)

def first_last_classes(element, first_class = "first", last_class = "last"):

    @when(element.ready_stage)
    def first_last_classes_handler(e):
        element = e.source
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

def rendering_xml():
    return get_current_rendering().renderer.outputs_xml

def rendering_html5():
    html_version = getattr(
        get_current_rendering().renderer,
        "html_version",
        None
    )
    return html_version >= 5

def html5_tag(element, tag):

    @when(element.ready_stage)
    def set_html5_alternative_tag(e):
        if rendering_html5():
            element.tag = tag

def html5_attr(element, key, value):

    @when(element.ready_stage)
    def set_html5_attribute(e):
        if rendering_html5():
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

_html5_sectioning_tags = set(["section", "article", "nav", "aside"])
_html5_headings = set(["h1", "h2", "h3", "h4", "h5", "h6"])
_html5_outline_root_regex = re.compile(r"\boutline_root\b")

def is_sectioning_content(tag):
    return tag in _html5_sectioning_tags

def add_html5_outline_classes(html):
    doc = bs4.BeautifulSoup(html, "lxml")

    def descend(node, level):
        if not isinstance(node, bs4.Tag):
            return

        css_class = node.get("class")

        if level is None:
            if css_class and "outline_root" in css_class:
                level = 1
        else:
            extra_class = None

            if node.name in _html5_sectioning_tags:
                extra_class = "s s%d" % level
                level += 1

            elif node.name in _html5_headings:
                extra_class = "h h%d" % (level + int(node.name[1]) - 1)

            if extra_class:
                if css_class:
                    node["class"] = css_class + [extra_class]
                else:
                    node["class"] = extra_class

        for child in node:
            descend(child, level)

    descend(doc, None)
    return str(doc)

inline_elements = {
    "b",
    "big",
    "i",
    "small",
    "tt",
    "abbr",
    "acronym",
    "cite",
    "code",
    "dfn",
    "em",
    "kbd",
    "strong",
    "samp",
    "time",
    "var",
    "a",
    "bdo",
    "br",
    "img",
    "map",
    "object",
    "q",
    "script",
    "span",
    "sub",
    "sup",
    "button",
    "input",
    "label",
    "select",
    "textarea"
}

def is_inline_element(tag):
    return tag in inline_elements

def serialize_value(value):
    if value is None:
        return ""
    elif isinstance(value, URL):
        return value.escape()
    elif isinstance(value, str):
        return value
    elif isinstance(value, (int, float, Decimal)):
        return str(value)
    else:
        raise ValueError("Can't serialize %r" % value)

