#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
import re
from xml.parsers import expat
from cocktail.modeling import refine, extend, call_base, getter, DictWrapper
from cocktail.translations import translations, get_language
from cocktail.html.element import default, PlaceHolder
from cocktail.html.templates.sourcecodewriter import SourceCodeWriter

WHITESPACE_EXPR = re.compile(r"\s*")

STRING_EXPR = re.compile(r"""
    (
        "{3}.*?"{3}     # Triple double quotes
      | '{3}.*?'{3}     # Triple single quotes
      | "(\\"|[^"])*"   # Double quotes
      | '(\\'|[^'])*'   # Single quotes
    )
    """, re.VERBOSE
)

LITERAL = 1
EXPRESSION = 2
PLACEHOLDER = 3

class TemplateCompiler(object):

    TEMPLATE_NS = "http://www.whads.com/ns/cocktail/templates"
    XHTML_NS = "http://www.w3.org/1999/xhtml"

    def __init__(self, pkg_name, class_name, loader, xml):
        
        self.pkg_name = pkg_name
        self.class_name = class_name
        self.loader = loader

        self.__classes = {}
        self.classes = DictWrapper(self.__classes)
        self.__class_names = set()
        self.__base_class_name = None
        self.__element_id = 0
        self.__stack = []
        self.__root_element_found = False
        self.__is_overlay = False
        self.__whitespace_stack = []
        
        self.__source_blocks = []
        
        self.__global_source_block = SourceCodeWriter()
        self.__source_blocks.append(self.__global_source_block)

        self.__declaration_source_block = SourceCodeWriter()
        self.__source_blocks.append(self.__declaration_source_block)

        self.__class_source_block = SourceCodeWriter(1)
        self.__source_blocks.append(self.__class_source_block)

        self.__end_source_block = SourceCodeWriter()

        self.__parser = expat.ParserCreate(namespace_separator = ">")

        for key in dir(self):
            if key.endswith("Handler"):
                setattr(self.__parser, key, getattr(self, key))
        
        self._push()
        self.compile(xml)
        self._pop()

    def compile(self, xml):        
        self.__parser.Parse(xml, True)

    def _parse_error(self, reason):
        raise ParseError(
            "Error parsing template %s.%s (line %d): %s" % (
                self.pkg_name,
                self.class_name,
                self.__parser.CurrentLineNumber + 1,
                reason
            )
        )

    def get_source(self):
        
        source = u"\n\n".join(
            unicode(block)
            for block in self.__source_blocks
        ) + u"\n"

        source += unicode(self.__end_source_block)
        return source

    def get_template_class(self):
        template_env = self.get_template_env()
        source = self.get_source()
        code = compile(
            source,
            "<%s.%s>" % (self.pkg_name, self.class_name),
            "exec"
        )
        exec code in template_env
        return template_env[self.class_name]

    def get_template_env(self):
        return {
            "pkg_name": self.pkg_name,
            "class_name": self.class_name,
            "loader": self.loader,
            "PlaceHolder": PlaceHolder,
            "translations": translations,
            "get_language": get_language,
            "refine": refine, # obsolete; use extend/call_base instead
            "extend": extend,
            "call_base": call_base
        }

    def add_class_reference(self, reference):
        
        name = self.__classes.get(reference)

        if name is None:
            name = reference.split(".")[-1]

            # Automatic class aliasing (avoid name collisions)
            if name in self.__class_names:
                
                generated_name = None
                suffix_id = 0

                while generated_name is None \
                or generated_name in self.__class_names:
                    suffix_id += 1
                    generated_name = "%s_%d" % (name + suffix_id)

                name = generated_name
            
            self.__class_names.add(name)
            self.__classes[reference] = name
            self.__global_source_block.write(
                "%s = loader.get_class('%s')" % (name, reference)
            )
        
        return name
    
    def _push(self):

        element = Frame()

        if self.__stack:
            element.source_block = self.__stack[-1].source_block
        else:
            element.source_block = self.__global_source_block

        self.__stack.append(element)
        return element

    def _pop(self):
        frame = self.__stack.pop()
        
        if self.__whitespace_stack:
            self.__whitespace_stack.pop()            

        for close_action in frame.close_actions:
            close_action()
        
        return frame

    def _get_parent_id(self):
        parent_id = None
                
        for frame in reversed(self.__stack):
            parent_id = frame.element
            if parent_id:
                return parent_id

        return None

    def StartElementHandler(self, name, attributes):
        
        frame = self._push()
        source = frame.source_block
        name_parts = name.split(">")
        is_content = True
        is_new = True
        elem_class_fullname = None
        element_expr = None
        factory_expr = None
        elem_tag = default
        parent_id = self._get_current_element()
        with_element = None
        with_def = None

        if len(name_parts) > 1:
            uri, tag = name_parts
        else:
            uri = None
            tag = name
        
        # Template/custom tag
        if uri == self.TEMPLATE_NS:

            if tag == "overlay":
                if self.__root_element_found:
                    self._parse_error(
                        "An overlay declaration can only be included at the "
                        "root of the document"
                    )
                self.__is_overlay = True

                overlay_class = attributes.pop(
                    self.TEMPLATE_NS + ">class",
                    None)
                
                if overlay_class:
                    self.__end_source_block.write(
                        "%s.register(%s)"
                        % (self.class_name, repr(overlay_class))
                    )

            elif tag in ("ready", "binding"):
                is_content = False
                is_new = False
                source.write("@%s.when_%s" % (parent_id, tag))
                source.write("def _handler():")
                source.indent()

                parent_id = self._get_parent_id()
                if parent_id:
                    source.write("element = " + parent_id)

                frame.close_actions.append(source.unindent)

            elif tag == "with":
                with_element = attributes.pop(
                    self.TEMPLATE_NS + ">element",
                    None)
                
                with_def = attributes.pop(
                    self.TEMPLATE_NS + ">def",
                    None)

                if not with_element and not with_def:
                    self._parse_error(
                        "'with' directive without an 'element' or 'def' "
                        "attribute"
                    )
                elif with_element and with_def:
                    self._parse_error(
                        "'with' directives can't have both 'element' and "
                        "'def' attributes"
                    )

                is_new = False

                if with_element:
                    element_expr = with_element

            elif tag == "new":
                
                element_expr = attributes.pop(
                    self.TEMPLATE_NS + ">element",
                    None)

                if not element_expr:
                    self._parse_error(
                        "'new' directive without an 'element' attribute"
                    )

            elif tag == "block":
                elem_class_fullname = "cocktail.html.Element"
                elem_tag = None
            else:
                elem_class_fullname = tag
        else:            
            elem_class_fullname = "cocktail.html.Element"
            elem_tag = tag

        if elem_class_fullname:
            elem_class_name = self.add_class_reference(elem_class_fullname)

        self._handle_conditions(attributes)
 
        if self.__whitespace_stack:
            ws = self.__whitespace_stack[-1]
            if ws:
                source.write('%s.append(%r)' % (parent_id, ws))
            self.__whitespace_stack[-1] = ""

        self.__whitespace_stack.append(None)

        # Document root
        if not self.__root_element_found:
            
            self.__root_element_found = True
            
            if self.__is_overlay:
                base_name = "Overlay"
                self.__global_source_block.write(
                    "from cocktail.modeling import call_base")
                self.__global_source_block.write(
                    "from cocktail.html import Overlay")
            else:
                base_name = elem_class_name

            self.__base_class_name = base_name 
            frame.element = id = "self"
            
            source = self.__declaration_source_block
            source.write("class %s(%s):" % (self.class_name, base_name))

            frame.source_block = source = SourceCodeWriter(1)
            self.__source_blocks.append(source)

            source.write("def _build(self):")
            source.indent()

            if self.__is_overlay:
                source.write("call_base()")
            else:
                source.write("%s._build(self)" % elem_class_name)
                if elem_tag is not default:
                    source.write("self.tag = %r" % elem_tag)

            self._handle_attributes(id, attributes)
        
        # Content
        elif is_content:

            # Iteration
            iter_expr = attributes.pop(self.TEMPLATE_NS + ">for", None)
        
            if iter_expr is not None:
                source.write("for " + iter_expr + ":")
                source.indent()
                frame.close_actions.append(source.unindent)

            # User defined names
            identifier = attributes.pop(self.TEMPLATE_NS + ">id", None)
            local_identifier = attributes.pop(self.TEMPLATE_NS + ">local_id", None)
            def_identifier = \
                attributes.pop(self.TEMPLATE_NS + ">def", None)
            
            if def_identifier:
                is_new = False
            
            # Instantiation
            if is_new or with_element:

                # Generate a name that can be used to uniquely reference the
                # element
                id = "_e" + str(self.__element_id)
                self.__element_id += 1
                frame.element = id

                source.write()

                # Elements with a user defined name get their own
                # factory method, which will be invoked to obtain a new
                # instance
                if identifier:
                    factory_expr = element_expr
                    element_expr = "self.create_%s()" % identifier
                
                # Normal class instantiation
                elif element_expr is None:
                    element_expr = "%s()" % elem_class_name

                source.write("element = %s = %s" % (id, element_expr))

                # Use the user defined name to bind elements to their
                # parents
                if identifier is not None and iter_expr is None:
                    source.write("self.%s = %s" % (identifier, id))

                if local_identifier is not None:
                    source.write("%s.%s = %s"
                        % (parent_id, local_identifier, id)
                    )

                # Parent and position
                parent = attributes.pop(self.TEMPLATE_NS + ">parent", None)
                index = attributes.pop(self.TEMPLATE_NS + ">index", None)
                after = attributes.pop(self.TEMPLATE_NS + ">after", None)
                before = attributes.pop(self.TEMPLATE_NS + ">before", None)
                
                if parent and index:
                    source.write("%s.insert(%s, %s)" % (parent, index, id))
                elif parent:
                    source.write("%s.append(%s)" % (parent, id))
                elif index:
                    source.write("%s.insert(%s, %s)" % (parent_id, index, id))
                elif after:
                    source.write("%s.place_after(%s)" % (id, after))
                elif before:
                    source.write("%s.place_before(%s)" % (id, before))
                elif is_new:
                    source.write("%s.append(%s)" % (parent_id, id))

            # Elements with a user defined identifier get their own factory
            # method, so that subclasses and containers can extend or override
            # it as needed
            factory_id = identifier or def_identifier or with_def

            if factory_id:
                
                frame.element = id = factory_id
                
                # Declaration
                args = attributes.pop(self.TEMPLATE_NS + ">args", None)

                if not args:
                    args = "*args, **kwargs"
                
                inline = ((with_def or def_identifier) and parent_id != "self")

                if inline:
                    self_var = parent_id
                    source.write("@extend(%s)" % parent_id)
                else:
                    self_var = "self"
                    source = SourceCodeWriter(1)
                    frame.source_block = source
                    self.__source_blocks.append(source)

                source.write(
                    "def create_%s(%s%s):"
                    % (factory_id, self_var, ", " + args if args else "")
                )
                source.indent()

                if with_def:
                    base_args = attributes.pop(
                        self.TEMPLATE_NS + ">baseargs", args)

                    if inline or self.__is_overlay:
                        element_factory = "call_base(%s)" % (base_args or "")
                    else:
                        element_factory = "%s.create_%s(self%s)" % (
                            self.__base_class_name,
                            factory_id,
                            ", " + base_args if base_args else ""
                        )
                else:
                    element_factory = factory_expr \
                                      or "%s()" % elem_class_name

                # Instantiation
                source.write("element = %s = %s" % (id, element_factory))
                
                @frame.closing
                def return_element():
                    source.write("return %s" % id)
                    source.unindent()
                
            # Attributes and properties
            if elem_tag is not default:
                source.write("%s.tag = %r" % (id, elem_tag))

            self._handle_attributes(id, attributes)

            # Automatically add the name of an element as one of its CSS
            # classes. Note this is done *after* assigning attribute values,
            # otherwise a 'class' attribute would overwrite this.
            if identifier or def_identifier or local_identifier:
                source.write("%s.add_class(%s)"
                    % (id, repr(factory_id or local_identifier))
                )
    
    def EndElementHandler(self, name):
        self._pop()
                
        # Persistent name
        frame = self.__stack[-1]
        frame.source_block.write("element = %s" % frame.element)
    
    def CharacterDataHandler(self, data):

        if data:

            # White space
            if not data.strip():
                if self.__whitespace_stack \
                and self.__whitespace_stack[-1] is not None:
                    self.__whitespace_stack[-1] += data
            else:
                parent_id = self._get_current_element()
                
                if self.__whitespace_stack:
                    self.__whitespace_stack[-1] = ""

                for chunk, expr_type in self._parse_data(data):

                    source = self.__stack[-1].source_block

                    if expr_type == LITERAL:
                        source.write('%s.append(%r)' % (parent_id, chunk))

                    elif expr_type == EXPRESSION:
                        source.write('%s.append(%s)' \
                            % (parent_id, chunk))
                    
                    elif expr_type == PLACEHOLDER:
                        source.write(
                            '%s.append(PlaceHolder(lambda: %s))'
                            % (parent_id, chunk)
                        )

    def DefaultHandler(self, data):

        for pi in ("<?py", "<?py-class"):
            if data.startswith(pi) and data[len(pi)] in (" \n\r\t"):                
                break
        else:
            return 
        
        data = data[len(pi) + 1:-2]
        lines = data.split("\n")
            
        for line in lines:
            if line.strip():
                indent_str = WHITESPACE_EXPR.match(line).group(0)
                break

        indent_end = len(indent_str)

        if pi == "<?py":
            source = self.__stack[-1].source_block

        elif pi == "<?py-class":
            source = self.__class_source_block

        for i, line in enumerate(lines):
            if not line.startswith(indent_str) and line.strip():
                self._parse_error("Inconsistent indentation on code block")
            line = line[indent_end:]
            source.write(line)

    def _get_current_element(self):
        for frame in reversed(self.__stack):
            if frame.element is not None:
                return frame.element

    def _handle_conditions(self, attributes):

        # Conditional blocks
        condition = attributes.pop(self.TEMPLATE_NS + ">if", None)

        if condition:
            condition_statement = "if " + condition + ":"
        else:
            condition = attributes.pop(self.TEMPLATE_NS + ">elif", None)

            if condition:
                condition_statement = "elif " + condition + ":"
            else:
                condition = attributes.pop(self.TEMPLATE_NS + ">else", None)

                if condition is not None:
                    if condition.strip():
                        self._parse_error("'else' directive must be empty")
                    condition_statement = "else:"
                else:
                    condition_statement = None

        if condition_statement:
            frame = self.__stack[-1]
            source = frame.source_block
            source.write(condition_statement)
            source.indent()
            frame.close_actions.append(source.unindent)

    def _handle_attributes(self, id, attributes):
        
        source = self.__stack[-1].source_block
        place_holders = None

        for key, value in attributes.iteritems():
            
            pos = key.find(">")

            if pos == -1:
                uri = None
                name = key
            else:
                uri = key[:pos]
                name = key[pos + 1:]

            is_template_attrib = (uri == self.TEMPLATE_NS)
            is_placeholder = False
            chunks = []

            for chunk, expr_type in self._parse_data(value):
                if expr_type == LITERAL:
                    chunks.append(repr(chunk))
                else:
                    is_placeholder = (expr_type == PLACEHOLDER)
                    chunks.append(chunk)
            
            value_source = " + ".join(chunks) or '""'

            if is_template_attrib:
                assignment = '%s.%s = %s' % (id, name, value_source)
            else:
                assignment = '%s["%s"] = %s' % (id, name, value_source)
            
            if is_placeholder:
                if place_holders is None:
                    place_holders = [assignment]
                else:
                    place_holders.append(assignment)
            else:
                source.write(assignment)

        if place_holders:
            source.write("@%s.when_binding" % id)
            source.write("def _bindings():")
            source.indent()

            parent_id = self._get_parent_id()
            if parent_id:
                source.write("element = " + parent_id)
                        
            if place_holders:
                for assignment in place_holders:
                    source.write(assignment)

            source.unindent()

    def _parse_data(self, data):

        i = 0
        start = 0
        depth = 0
        strlen = len(data)
        prevc = None
        expr_type = None
        
        while i < strlen:
            
            c = data[i]

            if c == "{":
                if not depth and (prevc == "$" or prevc == "@"):
                    if i != start and i - 1 > start:
                        yield data[start:i - 1], LITERAL

                    expr_type = prevc == "$" and EXPRESSION or PLACEHOLDER
                    depth += 1
                    start = i + 1

                elif depth:
                    depth += 1
                                        
                i += 1

            elif c == "}":
                depth -= 1
                
                if not depth:
                    if i > start:
                        yield data[start:i], expr_type
                    expr_type = None
                    start = i + 1

                i += 1

            else:
                match = STRING_EXPR.match(data, i)
                if match:
                    i = match.end()
                else:
                    i += 1

            prevc = c

        if i != start:
            yield data[start:], LITERAL


class Frame(object):

    def __init__(self, element = None):
        self.element = element
        self.close_actions = []

    def closing(self, func):
        self.close_actions.append(func)
        return func


class ParseError(Exception):
    pass

