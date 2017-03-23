#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
import re
from time import time
from json import dumps
from collections import OrderedDict
from lxml.etree import parse, QName, ProcessingInstruction
from cocktail.stringutils import normalize_indentation
from cocktail.modeling import OrderedSet
from cocktail.translations import translations
from cocktail.html.resources import (
    Resource,
    StyleSheet,
    EmbeddedResources,
    SASSCompilation
)
from cocktail.html.templates.sourcecodewriter import SourceCodeWriter
from .exceptions import ComponentFileError, ParseError

js_number_expr = re.compile(r"^[-+]?(\d+(\.\d*)?|(\d*\.)?\d+)$")


class ComponentLoader(object):

    __auto_name_counter = 0
    xmlns_ns = "http://www.w3.org/2000/xmlns"
    xhtml_ns = "http://www.w3.org/1999/xhtml"
    ui_ns = "http://www.whads.com/ns/cocktail/ui"
    style_inclusion = "link"

    tag_interfaces = {
        "a": "HTMLAnchorElement",
        "area": "HTMLAreaElement",
        "audio": "HTMLAudioElement",
        "br": "HTMLBRElement",
        "base": "HTMLBaseElement",
        "body": "HTMLBodyElement",
        "button": "HTMLButtonElement",
        "canvas": "HTMLCanvasElement",
        "dl": "HTMLDListElement",
        "data": "HTMLDataElement",
        "datalist": "HTMLDataListElement",
        "dialog": "HTMLDialogElement",
        #"div": "HTMLDivElement",
        "embed": "HTMLEmbedElement",
        "fieldset": "HTMLFieldSetElement",
        "form": "HTMLFormElement",
        "frameset": "HTMLFrameSetElement",
        "hr": "HTMLHRElement",
        "head": "HTMLHeadElement",
        "heading": "HTMLHeadingElement",
        "iframe": "HTMLIFrameElement",
        "img": "HTMLImageElement",
        "input": "HTMLInputElement",
        "keygen": "HTMLKeygenElement",
        "li": "HTMLLIElement",
        "label": "HTMLLabelElement",
        "legend": "HTMLLegendElement",
        "link": "HTMLLinkElement",
        "map": "HTMLMapElement",
        "meta": "HTMLMetaElement",
        "meter": "HTMLMeterElement",
        "ins": "HTMLModElement",
        "del": "HTMLModElement",
        "ol": "HTMLOListElement",
        "object": "HTMLObjectElement",
        "optgroup": "HTMLOptGroupElement",
        "option": "HTMLOptionElement",
        "output": "HTMLOutputElement",
        "p": "HTMLParagraphElement",
        "param": "HTMLParamElement",
        "picture": "HTMLPictureElement",
        "pre": "HTMLPreElement",
        "progress": "HTMLProgressElement",
        "blockquote": "HTMLQuoteElement",
        "q": "HTMLQuoteElement",
        "script": "HTMLScriptElement",
        "select": "HTMLSelectElement",
        "source": "HTMLSourceElement",
        "span": "HTMLSpanElement",
        "style": "HTMLStyleElement",
        "caption": "HTMLTableCaptionElement",
        "col": "HTMLTableColElement",
        "colgroup": "HTMLTableColElement",
        "td": "HTMLTableCellElement",
        "table": "HTMLTableElement",
        "th": "HTMLTableCellElement",
        "tr": "HTMLTableRowElement",
        "thead": "HTMLTableSectionElement",
        "tbody": "HTMLTableSectionElement",
        "tfoot": "HTMLTableSectionElement",
        "template": "HTMLTemplateElement",
        "textarea": "HTMLTextAreaElement",
        "time": "HTMLTimeElement",
        "title": "HTMLTitleElement",
        "track": "HTMLTrackElement",
        "ul": "HTMLUListElement",
        "video": "HTMLVideoElement"
    }

    def __init__(self, component, node = None):

        self.timestamp = time()
        self.component = component
        self.base_component = None
        self.dependencies = OrderedSet()
        self.subcomponents = {}
        self.is_module = False
        self.resources = OrderedSet()
        self.translation_keys = set()
        self.decorators = []
        self.properties = OrderedDict()
        self.source = SourceCodeWriter()
        self.head_source = None
        self.init_source = None
        self.init_tail_source = None
        self.body_source = None
        self.registration_source = None
        self.tail_source = None
        self.__stack = None
        self.__context_change_stack = []

        if node is None:
            try:
                document = parse(component.source_file)
            except IOError:
                raise ComponentFileError(component.full_name)
            node = document.getroot()

        if component.parent is None:
            translations.request_bundle(
                component.full_name.lower(),
                callback = (
                    lambda key, lang, value: self.translation_keys.add(key)
                ),
                reload = True
            )

        self.parse_document(node)

    def dispose(self):
        self.component = None
        self.base_component = None
        self.dependencies = None
        self.subcomponents = None
        self.resources = None
        self.translation_keys = None
        self.decorators = None
        self.properties = None
        self.source = None
        self.head_source = None
        self.init_source = None
        self.init_tail_source = None
        self.body_source = None
        self.registration_source = None
        self.tail_source = None
        self.__stack = None
        self.__context_change_stack = None

    def _auto_name(self):
        self.__auto_name_counter += 1
        return "_%d" % self.__auto_name_counter

    def parse_document(self, node):

        qname = QName(node.tag)
        local_name = qname.localname
        is_ui_node = (qname.namespace == self.ui_ns)
        inheriting_component = False

        if is_ui_node:
            if local_name == "module":
                self.is_module = True
            else:
                inheriting_component = True
                base_name = local_name
                self.base_component = self.component.registry.get(
                    base_name,
                    referrer = self.component,
                    reference_type = "base"
                )
        else:
            iface = self.tag_interfaces.get(local_name, "HTMLElement")
            base_name = "cocktail.ui.base." + iface

        if not self.is_module:
            self.source.write("{")
            self.source.indent()

        self.head_source = self.source.nest()

        if not self.is_module:

            # Component class declaration
            self.source.write(
                "let cls = class %s extends %s {" % (
                    self.component.name,
                    base_name
                )
            )
            self.body_source = self.source.nest(1)
            self.body_source.write("static get observedAttributes() { return this[cocktail.ui.OBSERVED_ATTRIBUTES]; }")
            self.source.write("}")

            # Component initializer
            self.body_source.write("initialize() {")
            self.init_source = self.body_source.nest(1)
            self.init_source.write("super.initialize();")
            self.init_source.write("let instance = this;")
            self.init_source.write(
                "this.classList.add('%s');"
                % self.component.css_class
            )
            self.init_tail_source = self.body_source.nest(1)
            self.body_source.write("}")

        self.registration_source = self.source.nest()
        self.tail_source = self.source.nest()
        self.parse_element(node)

        if not self.is_module:
            self.registration_source.write(
                "cocktail.ui.component({"
            )
            self.registration_source.indent()
            self.registration_source.write(
                "fullName: %s," % dumps(self.component.full_name)
            )
            self.registration_source.write(
                "cls: cls%s" % (
                    "," if not is_ui_node or self.decorators or self.properties else ""
                )
            )

            if not is_ui_node:
                self.registration_source.write(
                    "baseTag: %s%s" % (
                        dumps(local_name),
                        "," if self.decorators or self.properties else ""
                    )
                )

            if self.decorators:
                self.registration_source.write("decorators: [")
                self.registration_source.indent()

                for decorator in self.decorators[:-1]:
                    self.registration_source.write(decorator + ",")

                self.registration_source.write(self.decorators[-1])
                self.registration_source.unindent()
                self.registration_source.write(
                    "]," if self.properties else "]"
                )

            if self.properties:
                self.registration_source.write("properties: {")
                self.registration_source.indent()

                props = self.properties.items()
                for prop_name, prop_params in props[:-1]:
                    self.registration_source.write(
                        "%s: %s," % (prop_name, dumps(prop_params))
                    )

                self.registration_source.write(
                    "%s: %s," % (props[-1][0], dumps(props[-1][1]))
                )

                self.registration_source.unindent()
                self.registration_source.write("}")

            self.registration_source.unindent()
            self.registration_source.write("});")

        # Embed styles

        if not self.is_module:
            if self.style_inclusion == "embed":
                embedder = EmbeddedResources()
                css = []
                for resource in self.resources:
                    if isinstance(resource, StyleSheet):
                        css.append(embedder.get_resource_source(resource))
                if css:
                    with self.body_source.braces(
                        "static get embeddedStyles()"
                    ) as block:
                        block.write(
                            "return super.embeddedStyles + %s;"
                            % dumps(css)
                        )
            elif self.style_inclusion == "link":
                uris = [
                    resource.uri
                    for resource in self.resources
                    if isinstance(resource, StyleSheet)
                ]
                if uris:
                    with self.body_source.braces(
                        "static get linkedStyleSheets()"
                    ) as block:
                        block.write(
                            "return super.linkedStyleSheets.concat(%s);"
                            % dumps(uris)
                        )

        if not self.is_module:
            self.source.unindent()
            self.source.write("}")

    def parse_node(self, node):
        if node.tag is ProcessingInstruction:
            self.parse_processing_instruction(node)
        else:
            self.parse_element(node)

    def parse_element(self, element):

        node = StackNode()
        node.line_number = element.sourceline
        node.parent = self.__stack
        self.__stack = node
        qname = QName(element)
        local_name = qname.localname

        if node.parent:
            if node.parent.is_content:
                node.container = "this"
            elif node.parent.parent:
                node.container = node.parent.ref
            else:
                node.container = "this.shadowRoot"
        else:
            node.is_root = True

        if self.is_module and node.is_element:
            self.trigger_parser_error(
                "Modules can't contain elements: found %s" % local_name
            )

        node.is_ui_node = (qname.namespace == self.ui_ns)

        if node.is_ui_node:
            if local_name == "with":
                node.is_with_clause = True
            elif local_name == "content":
                node.is_content = True
            elif local_name == "property":
                node.is_property = True
            elif local_name == "translation":
                node.is_translation = True
            elif local_name == "requires-translation":
                node.is_translation_requirement = True
            elif local_name == "resource":
                node.is_resource = True
            elif local_name == "decoratedBy":
                node.is_decorator = True
            elif local_name == "requires":
                node.is_requirement = True

        node.is_element = (
            not node.is_content
            and not node.is_property
            and not node.is_resource
            and not node.is_decorator
            and not node.is_translation
            and not node.is_translation_requirement
            and not node.is_requirement
            and not self.is_module
        )
        node.is_new = (
            node.is_element
            and not node.is_root
            and not node.is_with_clause
        )
        node.is_component = (
            node.is_root
            or (node.is_new and node.is_ui_node)
            or node.is_with_clause
        )

        # Collect attributes
        attributes = dict(element.attrib)

        # Subcomponents
        subcomponent_name = attributes.pop("{%s}component" % self.ui_ns, None)
        if subcomponent_name:
            if node.is_root:
                if self.component.parent is None:
                    self.trigger_parser_error(
                        "Can't have a subcomponent as the document's root"
                    )
            else:
                subcomponent = self.component.registry._subcomponent(
                    self.component,
                    subcomponent_name
                )
                subcomponent.load(element)
                self.subcomponents[subcomponent_name] = subcomponent
                return

        # Placement
        node.placement = attributes.pop("{%s}placement" % self.ui_ns, "append")

        if node.placement not in ("append", "none"):
            self.trigger_parser_error(
                "'placement' should be one of 'append' or 'none', "
                "got '%s' instead"
                % node.placement
            )

        # With
        if node.is_with_clause:
            if node.is_root:
                self.trigger_parser_error(
                    "Can't have a 'with' clause as the document's root"
                )
            node.id = attributes.pop("{%s}element" % self.ui_ns, None)
            if not node.id:
                self.trigger_parser_error(
                    "'with' clause without an 'element' attribute"
                )
            node.ref = node.parent.ref + "." + node.id

        # Property
        elif node.is_property:
            node.prop_name = attributes.pop("name", None)
            if not node.prop_name:
                self.trigger_parser_error(
                    "'property' clause without a 'name' attribute"
                )

            prop_options = {}

            reflected = attributes.pop("reflected", "false")
            if reflected == "true":
                prop_options["reflected"] = True
            elif reflected == "false":
                pass
            else:
                self.trigger_parser_error(
                    "Invalid value for 'reflected': expected true or false, "
                    "got %s instead"
                    % reflected
                )

            prop_type = attributes.pop("type", None)
            if prop_type:
                prop_options["type"] = prop_type

            default = attributes.pop("default", None)
            if default:
                self.init_tail_source.write(
                    "this.setAttribute('%s', %s);"
                    % (node.prop_name, dumps(default))
                )

            self.properties[node.prop_name] = prop_options

        # Translations
        # Translation keys
        elif node.is_translation or node.is_translation_requirement:

            if node.is_root:
                self.trigger_parser_error(
                    "Can't have a 'translation' clause as the document root"
                )

            key = self.component.full_name
            custom_key = attributes.pop("key", None)

            if custom_key:
                if custom_key.startswith("."):
                    key += custom_key
                else:
                    key = custom_key
            else:
                if not node.parent.id:
                    self.trigger_parser_error(
                        "A 'translation' clause without an explicit "
                        "translation key is only allowed on an element with "
                        "an id"
                    )
                if self.__context_change_stack:
                    key += "." + ".".join(self.__context_change_stack)
                key += "." + node.parent.id

            self.translation_keys.add(key)

            if node.is_translation:
                self.init_source.write(
                    "cocktail.ui.insertTranslation(%s, '%s');"
                    % (node.parent.ref, key)
                )

        # Resource
        elif node.is_resource:
            uri = attributes.pop("href", None)
            if not uri:
                self.trigger_parser_error(
                    "'resource' clause without an 'href' attribute"
                )
            resource = Resource.from_uri(uri)
            self.resources.append(resource)

        # Decorator
        elif node.is_decorator:

            if not node.parent or not node.parent.is_root:
                self.trigger_parser_error(
                    "'decoratedBy' directives must be placed directly descend "
                    "from a component's root element"
                )

            function = attributes.pop("function", None)
            if not function:
                self.trigger_parser_error(
                    "'decoratedBy' clause without a 'function' attribute"
                )

            self.decorators.append(function)

        # Requirement
        elif node.is_requirement:
            dep_name = attributes.pop("component", None)
            if not dep_name:
                self.trigger_parser_error(
                    "'requirement' clause without a 'component' attribute"
                )
            dependency = self.component.registry.get(
                dep_name,
                referrer = self.component,
                reference_type = "dependency"
            )
            self.dependencies.append(dependency)

        # Element ID
        else:
            node.id = attributes.pop("id", None)

            if node.id and node.is_root:
                self.trigger_parser_error("Can't give an id to the root element")

            # Name generation
            if node.is_root:
                node.ref = "this"
            else:
                node.ref = node.id and "this." + node.id or self._auto_name()

        if node.is_with_clause and node.parent and node.parent.id:
            self.__context_change_stack.append(node.parent.id)

        # Instantiation
        if node.is_new:

            # Components
            if node.is_ui_node:
                # Other component (dotted name)
                if "." in local_name:
                    instantiation = "%s.create()" % local_name
                    self.dependencies.append(
                        self.component.registry.get(
                            local_name,
                            referrer = self.component,
                            reference_type = "part"
                        )
                    )
                # Subcomponent
                else:
                    instantiation = "this.constructor.%s.create()" % local_name

            # Regular elements
            else:
                instantiation = "document.createElement('%s')" % local_name

            if node.id:
                self.init_source.write(
                    "%s = %s;" % (node.ref, instantiation)
                )
                self.init_source.write(
                    "%s.id = '%s';" % (node.ref, node.id)
                )
            else:
                self.init_source.write(
                    "let %s = %s;" % (node.ref, instantiation)
                )

        if node.is_element:
            node.after_declaration_source = self.init_source.nest()

        # Assign attributes
        for attrib_name, attrib_value in attributes.iteritems():

            attrib_qname = QName(attrib_name)
            attrib_name = attrib_qname.localname
            attrib_ns = qname.namespace

            if node.is_property:
                self.trigger_parser_error(
                    "Invalid attribute '%s' on a 'property' clause"
                    % attrib_name
                )

            if attrib_name == "xmlns":
                continue

            if self.is_module:
                self.trigger_parser_error("Modules can't have attributes")

            if attrib_ns is None or attrib_ns in (self.xhtml_ns, self.ui_ns):
                self.init_tail_source.write(
                    '%s.setAttribute("%s", "%s");'
                    % (node.ref, attrib_name, attrib_value)
                )

        # Add text
        if element.text and element.text.strip():
            self.init_source.write(
                "%s.appendChild(document.createTextNode(%s));"
                % (node.ref, dumps(element.text))
            )

        # Add tail text
        if element.tail and element.tail.strip():
            node.parent.write(
                "%s.appendChild(document.createTextNode(%s));"
                % (node.parent.ref, dumps(element.tail))
            )

        # Process child elements
        for child in element:
            child_name = self.parse_node(child)

        # Append child elements to their parents
        if node.is_new and node.container and node.placement == "append":
            self.init_source.write(
                "%s.appendChild(%s);" % (node.container, node.ref)
            )

        self.__stack = self.__stack.parent

        if node.is_with_clause and node.parent and node.parent.id:
            self.__context_change_stack.pop(-1)

    def parse_processing_instruction(self, pi):

        target = pi.target

        # Inlined javascript blocks
        if target == "js":
            value = normalize_indentation(pi.text.rstrip())
            if self.__stack:
                value = (
                    "{let element = %s; %s}"
                    % (self.__stack.ref, value)
                )
            self.init_source.write(value)

        # Javascript blocks for the module head
        elif target == "head":
            value = normalize_indentation(pi.text.rstrip())
            self.head_source.write(value)

        # Javascript blocks for the class body
        elif target == "class":
            value = normalize_indentation(pi.text.rstrip())
            self.body_source.write(value)

        # Javascript blocks for the module head
        elif target == "tail":
            value = normalize_indentation(pi.text.rstrip())
            self.tail_source.write(value)

        # Event listeners
        elif target == "on":
            event = pi.text.split(None, 1)[0]
            listener = pi.text[len(event):].rstrip()
            listener = normalize_indentation(listener.rstrip())

            if self.__stack.is_property:
                ref = self.__stack.parent.ref
                event = self.__stack.prop_name + event[0].upper() + event[1:]
                source = self.__stack.parent.after_declaration_source
            else:
                ref = self.__stack.ref
                source = self.__stack.after_declaration_source

            with source.indented_block(
                "%s.addEventListener('%s', function (e) {" % (ref, event),
                "});"
            ) as b:
                if self.__stack.is_property:
                    b.write("let oldValue = e.detail.oldValue;")
                    b.write("let newValue = e.detail.newValue;")

                b.write(listener)

        # Inline SCSS
        elif target == "css":
            scss = normalize_indentation(pi.text.rstrip())

            if not self.__stack.is_root:
                if not self.__stack.id:
                    self.trigger_parser_error(
                        "Inline css can only be added to a component root or "
                        "to elements with an ID"
                    )
                scss = "#%s { %s }" % (self.__stack.id, scss)

            sass_compilation = SASSCompilation()
            css = sass_compilation.compile(string = scss)
            self.init_source.write_lines(
                "let styles = document.createElement('style');",
                "styles.type = 'text/css';",
                "styles.textContent = %s;" % (dumps(css),),
                "cocktail.ui.getShadow(%s).appendChild(styles);"
                % self.__stack.ref
            )

    def trigger_parser_error(self, message):

        if self.__stack:
            line_number = self.__stack.line_number
        else:
            line_number = None

        raise ParseError(self, message, line_number = line_number)


class StackNode(object):

    # The line number that originated this node in the XML file
    line_number = None

    # The previous element in the stack
    parent = None

    # If the node represents an element, the name explicitly given to that
    # element (through an ui:id attribute)
    id = None

    # If the node represents an element, a javascript expression pointing to
    # that element, in the context of its owning component
    ref = None

    # If the node represents an element, a javascript expression pointing to
    # the element where the element should be inserted
    container = None

    # Wether the node is a <ui:> element
    is_ui_node = False

    # Wether the node is a <ui:with> clause
    is_with_clause = False

    # Wether the node is a <ui:content> clause
    is_content = False

    # Wether the node is a property declaration
    is_property = False

    # Wether the node is a translation insertion point
    is_translation = False

    # Wether the node is a translation dependency declaration
    is_translation_requirement = False

    # Wether the node is a requirement declaration
    is_requirement = False

    # If the node represents a property, this attribute will contain its name
    # (otherwise it will be None)
    prop_name = None

    # Wether the node is a resource inclusion
    is_resource = False

    # Wether the node is a reference to a decorator (a function modifying the
    # resulting component)
    is_decorator = False

    # Wether the node represents a DOM element in the component
    is_element = False

    # If the node represents a DOM element (is_element = True), wether said
    # element is a new node or a reference to an existing one (so is_new will
    # be False on <ui:with> clauses)
    is_new = False

    # Wether the node represents an element based on a component
    is_component = False

    # Wether the node represents a component's root element
    is_root = False

    # The insertion point / method for the element. One of "append" (default)
    # or "none". Set with the ui:placement attribute.
    placement = None

    # A SourceCodeWriter that allows inserting code right after the element is
    # declared (required to register event listeners before property
    # assignments)
    after_declaration_source = None

