#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
import re
from time import time
from json import dumps
from xml.dom.minidom import parse
from cocktail.modeling import OrderedSet
from cocktail.translations import translations
from cocktail.html import Resource
from cocktail.html.templates.sourcecodewriter import SourceCodeWriter

js_number_expr = re.compile(r"^[-+]?(\d+(\.\d*)?|(\d*\.)?\d+)$")


class ComponentLoader(object):

    __auto_name_counter = 0
    xhtml_ns = "http://www.w3.org/1999/xhtml"
    ui_ns = "http://www.whads.com/ns/cocktail/ui"

    def __init__(self, component, node = None):

        self.timestamp = time()
        self.component = component
        self.base_component = None
        self.dependencies = OrderedSet()
        self.subcomponents = {}
        self.is_module = False
        self.resources = OrderedSet()
        self.translation_keys = set()
        self.source = SourceCodeWriter()
        self.build_source = None
        self.__element_stack = []
        self.__component_stack = []
        self.__context_change_stack = []

        if node is None:
            document = parse(component.source_file)
            node = document.documentElement

        if component.parent is None:
            translations.request_bundle(
                component.full_name.lower(),
                callback = (
                    lambda key, lang, value: self.translation_keys.add(key)
                )
            )

        self.parse_document(node)

    def dispose(self):
        self.component = None
        self.base_component = None
        self.dependencies = None
        self.subcomponents = None
        self.resources = None
        self.translation_keys = None
        self.source = None
        self.build_source = None
        self.__element_stack = None
        self.__component_stack = None
        self.__context_change_stack = None

    def _auto_name(self):
        self.__auto_name_counter += 1
        return "_%d" % self.__auto_name_counter

    def parse_document(self, node):

        is_ui_node = (node.namespaceURI == self.ui_ns)

        if is_ui_node:
            if node.localName == "module":
                self.is_module = True
            else:
                base_name = node.localName
                self.base_component = self.component.registry.get(base_name)
        else:
            base_name = "cocktail.ui.Component"

        if not self.is_module:
            self.source.write(
                "%s.extend('%s', function () {" % (
                    base_name,
                    self.component.full_name
                )
            )
            self.build_source = self.source.nest(1)

        self.parse_element(node)

        if not self.is_module:
            if self.component.parent:
                self.source.write(
                    "}, %s);\n"
                    % self.component.parent.full_name
                )
            else:
                self.source.write("});\n")

    def parse_node(self, node):
        if node.nodeType == 1:
            self.parse_element(node)
        elif node.nodeType == 7:
            self.parse_processing_instruction(node)

    def parse_element(self, node):

        if self.__element_stack:
            parent_id, parent_name = self.__element_stack[-1]
            parent_component = self.__component_stack[-1]
            is_root = False
        else:
            parent_id = None
            parent_name = None
            parent_component = None
            is_root = True

        if self.is_module and not is_root:
            self.trigger_parser_error("Modules can't contain elements")

        is_ui_node = (node.namespaceURI == self.ui_ns)
        is_with_clause = (is_ui_node and node.localName == "with")
        is_new = not is_with_clause and not self.is_module

        # Collect attributes
        attributes = {}
        for i in range(node.attributes.length):
            a = node.attributes.item(i)
            attributes[(a.namespaceURI, a.localName)] = a.nodeValue

        # Subcomponents
        subcomponent_name = attributes.pop((self.ui_ns, "component"), None)
        if subcomponent_name:
            if is_root:
                if self.component.parent is None:
                    self.trigger_parser_error(
                        "Can't have a subcomponent as the document's root"
                    )
            else:
                subcomponent = self.component.registry._subcomponent(
                    self.component,
                    subcomponent_name
                )
                subcomponent.load(node)
                self.subcomponents[subcomponent_name] = subcomponent
                return

        # Element ID
        if is_with_clause:
            if not parent_name:
                self.trigger_parser_error(
                    "Can't have a 'with' clause as the document's root"
                )
            id = attributes.pop((self.ui_ns, "element"), None)
            if not id:
                self.trigger_parser_error(
                    "'with' clause without an 'element' attribute"
                )
            is_part = False
            name = parent_name + "." + id
        else:
            id = attributes.pop((self.ui_ns, "id"), None)

            if id and is_root:
                self.trigger_parser_error("Can't give an id to the root element")

            is_part = bool(id and parent_name)

            # Name generation
            if is_root:
                name = "instance"
            else:
                name = id or self._auto_name()

        self.__element_stack.append((id, name))

        if is_ui_node or is_root:
            self.__component_stack.append(name)

        if is_with_clause and parent_id:
            self.__context_change_stack.append(parent_id)

        # Instantiation
        if is_new:

            # Components
            if is_ui_node:
                if is_root:
                    instantiation = (
                        "%s.createInstance()" % node.localName
                    )
                else:
                    # Other component (dotted name)
                    if "." in node.localName:
                        instantiation = "%s()" % node.localName
                        self.dependencies.append(
                            self.component.registry.get(node.localName)
                        )
                    # Subcomponent
                    else:
                        instantiation = "%s.%s()" % (
                            parent_component,
                            node.localName
                        )

            # Regular elements
            else:
                instantiation = "'%s'" % node.nodeName

            if is_root:
                self.build_source.write(
                    "let %s = cocktail.ui._root(this, %s);"
                    % (name, instantiation)
                )
            else:
                self.build_source.write(
                    "let %s = cocktail.ui._elem(instance, %s, %s);"
                    % (name, dumps(id), instantiation)
                )

        # Assign attributes
        for (attrib_ns, attrib_name), attrib_value in attributes.iteritems():

            if attrib_name == "xmlns":
                continue

            if self.is_module:
                self.trigger_parser_error("Modules can't have attributes")

            if attrib_ns == self.ui_ns:
                self.build_source.write(
                    '%s.%s = %s;'
                    % (
                        name,
                        attrib_name,
                        self.get_javascript_expression(attrib_value)
                    )
                )
            elif attrib_ns == self.xhtml_ns or not attrib_ns:
                self.build_source.write(
                    '%s.setAttribute("%s", "%s");'
                    % (name, attrib_name, attrib_value)
                )

        # Process child elements
        for child in node.childNodes:
            child_name = self.parse_node(child)

        # Append child elements to their parents
        if not self.is_module:
            if is_with_clause:
                pass
            elif parent_name:
                self.build_source.write(
                    "cocktail.ui.add(%s, %s);" % (parent_name, name)
                )
            else:
                self.build_source.write("return %s;" % name)

        self.__element_stack.pop(-1)

        if is_ui_node:
            self.__component_stack.pop(-1)

        if is_with_clause and parent_id:
            self.__context_change_stack.pop(-1)

    def parse_processing_instruction(self, node):

        value = node.data.strip()

        # Linked scripts & stylesheets
        if node.target == "resource":
            resource = Resource.from_uri(value)
            self.resources.append(resource)

        # Translation keys
        elif node.target in ("translation", "requires-translation"):

            key = self.component.full_name
            id, name = self.__element_stack[-1]

            if value:
                key += "." + value
            elif len(self.__element_stack) > 1:
                if not id:
                    self.trigger_parser_error(
                        "A <?translation instruction without an explicit "
                        "translation key is only allowed on an element with "
                        "an id"
                    )
                if self.__context_change_stack:
                    key += "." + ".".join(self.__context_change_stack)
                key += "." + id

            self.translation_keys.add(key)

            if node.target == "translation":
                self.build_source.write(
                    "cocktail.ui.insertTranslation(%s, '%s');"
                    % (name, key)
                )

        # Inlined javascript blocks
        elif node.target == "js":
            if self.__element_stack:
                value = (
                    "let element = %s; %s"
                    % (self.__element_stack[-1][1], value)
                )
            self.build_source.write(value)

        # Explicit component dependencies
        elif node.target == "requires":
            dependency = self.component.registry.get(value)
            self.dependencies.append(dependency)

    def get_javascript_expression(self, value):

        if value in ("true", "false", "null", "undefined", "NaN"):
            return value
        elif value.startswith("js:"):
            return dumps(value[3:])
        elif value.startswith("str:"):
            return dumps(value[4:])
        elif js_number_expr.match(value):
            return value
        elif value.startswith("[") and value.endswith("]"):
            return value
        elif value.startswith("{") and value.endswith("}"):
            return value

        return dumps(value)

    def trigger_parser_error(self, message):
        raise ParseError(self, message)


class ParseError(Exception):

    def __init__(self, component_loader, message):
        self.message = message
        self.component_loader = component_loader

    def __str__(self):
        return "%s (at component %s)" % (
            self.message,
            self.component_loader.component.full_name
        )

