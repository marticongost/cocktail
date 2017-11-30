#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
import re
from time import time
from collections import OrderedDict
from lxml.etree import parse, QName, ProcessingInstruction
from cocktail.javascriptserializer import dumps, JS
from cocktail.stringutils import normalize_indentation
from cocktail.modeling import OrderedSet
from cocktail.translations import translations
from cocktail.html.resources import (
    Resource,
    StyleSheet,
    EmbeddedResources,
    SASSCompilation,
    resource_repositories
)
from cocktail.sourcecodewriter import SourceCodeWriter
from .exceptions import ComponentFileError, ParseError

js_number_expr = re.compile(r"^[-+]?(\d+(\.\d*)?|(\d*\.)?\d+)$")
js_identifier_expr = re.compile(r"[a-z][a-z0-9_]*")


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
        self.symbols_source = None
        self.init_source = None
        self.init_tail_source = None
        self.body_source = None
        self.declaration_source = None
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
            self.require_translation_bundle(component.full_name.lower())

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
        self.symbols_source = None
        self.init_source = None
        self.init_tail_source = None
        self.body_source = None
        self.declaration_source = None
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
                if base_name[0].isupper():
                    if self.component.parent:
                        base_name = self.component.parent.full_name + "." + base_name
                    else:
                        self.trigger_parser_error(
                            "Subcomponent reference not valid in this context"
                        )

                self.base_component = self.component.registry.get(
                    base_name,
                    referrer = self.component,
                    reference_type = "base"
                )
        else:
            base_name = self.tag_interfaces.get(local_name, "HTMLElement")
            base_name = "cocktail.ui.base.%s" % base_name

        if not self.is_module:
            self.source.write("{")
            self.source.indent()

        self.symbols_source = self.source.nest()
        self.head_source = self.source.nest()

        if not self.is_module:

            # Component class declaration
            with self.source.braces("let cls = cocktail.ui.component(", ");"):
                self.declaration_source = self.source.nest()

                self.body_source = self.source.nest(1)
                self.body_source.write(
                    "static get observedAttributes() { "
                    "return cocktail.ui._getObservedAttributes(this); }"
                )

                if not self.component.parent:
                    self.body_source.write(
                        "static get requiresShadowDOM() { return true; }"
                    )

                # Component initializer
                self.body_source.write("initialize() {")
                self.init_source = self.body_source.nest(1)
                self.init_source.write("super.initialize();")
                self.init_source.write("let instance = this;")
                self.init_source.write(
                    "this.classList.add('%s');"
                    % self.component.css_class
                )
                if self.component.parent:
                    self.init_source.write(
                        "this.classList.add('%s');" % self.component.name
                    )
                self.init_tail_source = self.body_source.nest(1)
                self.body_source.write("}")

                self.source.write("}")

        self.tail_source = self.source.nest()
        self.parse_element(node)

        if not self.is_module:

            self.declaration_source.write(
                "fullName: %s," % dumps(self.component.full_name)
            )

            if self.component.parent:
                self.declaration_source.write(
                    "parentComponent: %s," % self.component.parent.full_name
                )

            if not is_ui_node:
                self.declaration_source.write(
                    "baseTag: %s," % dumps(local_name)
                )

            base_expr = base_name

            for decorator in self.decorators:
                base_expr = "%s(%s)" % (decorator, base_expr)

            self.declaration_source.write(
                "cls: class %s extends %s {" % (
                    self.component.name,
                    base_expr
                )
            )

            with self.body_source.braces(
                "static get componentProperties()"
            ) as b:
                if self.properties:
                    with b.braces("return", ";") as b:
                        props = self.properties.items()
                        for prop_name, prop_params in props[:-1]:
                            b.write(
                                "%s: %s," % (prop_name, dumps(prop_params))
                            )

                        b.write(
                            "%s: %s" % (props[-1][0], dumps(props[-1][1]))
                        )
                else:
                    b.write("return {};")

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
            elif self.component.parent:
                node.container = "this"
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
            elif local_name == "symbol":
                node.is_symbol = True
            elif local_name == "translation":
                node.is_translation = True
            elif local_name == "requires-translation":
                node.is_translation_requirement = True
            elif local_name == "requires-translation-bundle":
                node.is_translation_bundle_requirement = True
            elif local_name == "resource":
                node.is_resource = True
            elif local_name == "decoratedBy":
                node.is_decorator = True
            elif local_name == "requires":
                node.is_requirement = True

        node.is_element = (
            not node.is_content
            and not node.is_property
            and not node.is_symbol
            and not node.is_resource
            and not node.is_decorator
            and not node.is_translation
            and not node.is_translation_requirement
            and not node.is_translation_bundle_requirement
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
                self.__stack = self.__stack.parent
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
                if not js_identifier_expr.match(prop_type):
                    prop_type = JS(prop_type)
                prop_options["type"] = prop_type

            default = attributes.pop("default", None)
            if default:
                self.init_tail_source.write(
                    "this.setAttribute('%s', %s);"
                    % (node.prop_name, dumps(default))
                )

            final = attributes.pop("final", "false")
            if final == "true":
                prop_options["isFinal"] = True
            elif final == "false":
                pass
            else:
                self.trigger_parser_error(
                    "Invalid value for 'final': expected true or false, "
                    "got %s instead"
                    % final
                )

            event_is_composed = attributes.pop("eventIsComposed", "false")
            if event_is_composed == "true":
                prop_options["eventIsComposed"] = True
            elif event_is_composed == "false":
                pass
            else:
                self.trigger_parser_error(
                    "Invalid value for 'eventIsComposed': "
                    "expected true or false, got %s instead"
                    % event_is_composed
                )

            event_bubbles = attributes.pop("eventBubbles", "false")
            if event_bubbles == "true":
                prop_options["eventBubbles"] = True
            elif event_bubbles == "false":
                pass
            else:
                self.trigger_parser_error(
                    "Invalid value for 'eventBubbles': "
                    "expected true or false, got %s instead"
                    % event_bubbles
                )

            self.properties[node.prop_name] = prop_options

        # Symbols
        elif node.is_symbol:
            symbol_name = attributes.pop("name", None)
            if not symbol_name:
                self.trigger_parser_error("symbol without a 'name' attribute")

            symbol_component = None
            while symbol_name and symbol_name[0] == ".":
                symbol_name = symbol_name[1:]
                if symbol_component is None:
                    symbol_component = self.component
                else:
                    symbol_component = symbol_component.parent

            if symbol_component is None:
                symbol_component = self.component

            node.symbol_name = symbol_name
            node.symbol_full_name = symbol_component.full_name + "." + symbol_name

            self.symbols_source.write(
                "const %s = Symbol.for('%s');"
                % (
                    node.symbol_name,
                    node.symbol_full_name
                )
            )

        # Translation bundles
        elif node.is_translation_bundle_requirement:
            bundle = attributes.pop("name", None)

            if not bundle:
                self.trigger_parser_error(
                    "requires-translation-bundle without a 'name' attribute"
                )

            self.require_translation_bundle(bundle)

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
                translation_attribute = attributes.pop("attribute", None)
                if translation_attribute:
                    self.init_source.write(
                        "%s.setAttribute(%s, cocktail.ui.translations[%s]);"
                        % (
                            node.parent.ref,
                            dumps(translation_attribute),
                            dumps(key)
                        )
                    )
                else:
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
            type = attributes.pop("type", None)
            resource = Resource.from_uri(uri, mime_type = type)
            if node.parent.is_root or not isinstance(resource, StyleSheet):
                self.resources.append(resource)
            else:
                self.insert_stylesheet(node.parent, resource)

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
                if self.component.parent:
                    self.init_source.write(
                        "%s.classList.add('%s');" % (node.ref, node.id)
                    )
                else:
                    self.init_source.write(
                        "%s.id = '%s';" % (node.ref, node.id)
                    )
            else:
                self.init_source.write(
                    "let %s = %s;" % (node.ref, instantiation)
                )

        if node.is_element:
            node.after_declaration_source = self.init_source.nest()

        # Inject the theme's stylesheet for the element
        if node.is_element:
            theme = self.component.registry.theme
            sheet = None

            if node.is_root:
                if not self.component.parent:
                    sheet = theme.get_stylesheet(self.component)
                    if sheet:
                        self.resources.append(sheet)
            elif (
                node.is_component
                and node.is_new
                and node.id
            ):
                sheet = theme.get_stylesheet(self.component, node.id)
                if sheet:
                    self.insert_stylesheet(node, sheet)

        # Assign attributes
        for attrib_name, attrib_value in attributes.iteritems():

            attrib_qname = QName(attrib_name)
            attrib_name = attrib_qname.localname
            attrib_ns = qname.namespace

            if node.is_property or node.is_symbol:
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
            self.init_source.write(
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
            with self.init_source.braces():
                if self.__stack:
                    self.init_source.write("let element = %s;" % self.__stack.ref)
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
            event_parts = event.split(":")

            if len(event_parts) == 1:
                if self.__stack.is_property:
                    is_property = True
                    ref = self.__stack.parent.ref
                    event = (
                        self.__stack.prop_name
                        + event[0].upper()
                        + event[1:]
                    )
                    source = self.__stack.parent.after_declaration_source
                else:
                    is_property = False
                    ref = self.__stack.ref
                    source = self.__stack.after_declaration_source

            elif len(event_parts) == 2:
                is_property = True
                property, event = event_parts
                event = property + event[0].upper() + event[1:]
                ref = self.__stack.ref
                source = self.__stack.after_declaration_source
            else:
                self.trigger_parser_error("Invalid event name")

            with source.indented_block(
                "%s.addEventListener('%s', function (e) {" % (ref, event),
                "});"
            ) as b:
                if is_property:
                    b.write("let oldValue = e.detail.oldValue;")
                    b.write("let newValue = e.detail.newValue;")

                b.write(listener)

        # Window event listeners
        elif target == "on-window":
            event, listener = pi.text.strip().split(None, 1)
            with self.init_source.indented_block(
                "instance.addWindowListener(%s, (e) => {" % dumps(event),
                "}, %s)" % self.__stack.ref
            ) as block:
                block.write(listener)

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

        # Inline SVG
        elif target == "svg":

            url = pi.text.strip()
            path = resource_repositories.locate(url)

            if not path:
                self.trigger_parser_error("Can't locale SVG file %s" % url)

            try:
                with open(path) as svg_file:
                    svg = svg_file.read()
            except Exception, e:
                self.trigger_parser_error(
                    "Error opening SVG file %s: %s" % (url, e)
                )

            self.init_source.write(
                "%s.appendChild("
                "new DOMParser().parseFromString("
                "%s, 'image/svg+xml').documentElement)"
                % (self.__stack.ref, dumps(svg))
            )

    def insert_stylesheet(self, node, resource):

        with self.init_source.braces() as block:

            if self.style_inclusion == "embed":
                embedder = EmbeddedResources()
                css = embedder.get_resource_source(resource)
                block.write(
                    "let styleSheet = "
                    "document.createElement('style');"
                )
                block.write("styleSheet.type = 'text/css';")
                block.write("styleSheet.innerText = %s;" % dumps(css))
            elif self.style_inclusion == "link":
                block.write(
                    "let styleSheet = "
                    "document.createElement('link');"
                )
                block.write("styleSheet.rel = 'stylesheet';")
                block.write("styleSheet.type = 'text/css';")
                block.write(
                    "styleSheet.href = %s;" % dumps(resource.uri)
                )

            block.write("%s.shadowRoot.appendChild(styleSheet);" % node.ref)

    def require_translation_bundle(self, bundle):
        translations.request_bundle(
            bundle,
            callback = (
                lambda key, lang, value: self.translation_keys.add(key)
            ),
            reload = True
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

    # Wether the node is a symbol declaration
    is_symbol = False

    # Wether the node is a translation insertion point
    is_translation = False

    # Wether the node is a translation dependency declaration
    is_translation_requirement = False

    # Wether the node is a translation bundle dependency declaration
    is_translation_bundle_requirement = False

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

