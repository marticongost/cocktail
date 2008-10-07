#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
import re
from xml.parsers import expat
from cocktail.modeling import getter, DictWrapper
from cocktail.html.element import default
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
        self.__element_id = 0
        self.__stack = []
        self.__root_element_found = False
        self.__context_is_current = False
        self.__source_blocks = []
        self.__global_source_block = SourceCodeWriter()
        self.__source_blocks.append(self.__global_source_block)
        self.__parser = expat.ParserCreate(namespace_separator = ">")

        for key in dir(self):
            if key.endswith("Handler"):
                setattr(self.__parser, key, getattr(self, key))
        
        self._push()
        self.compile(xml)
        self._pop()

    def compile(self, xml):        
        self.__parser.Parse(xml, True)

    def get_source(self):
        
        return u"\n\n".join(
            unicode(block)
            for block in self.__source_blocks
        ) + u"\n"

    def get_template_class(self):

        template_scope = {
            "pkg_name": self.pkg_name,
            "class_name": self.class_name,
            "loader": self.loader
        }

        source = self.get_source()
        print source
        exec source in template_scope
        return template_scope[self.class_name]

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
        self.__context_is_current = False
        return element

    def _pop(self):
        self.__context_is_current = False
        frame = self.__stack.pop()

        for close_action in frame.close_actions:
            close_action()
        
        return frame

    def StartElementHandler(self, name, attributes):
        
        frame = self._push()
        source = frame.source_block
        name_parts = name.split(">")
        is_content = True
        is_new = True
        elem_class_fullname = None
        element_factory = None
        elem_tag = default
        parent_id = self._get_current_element()

        if len(name_parts) > 1:
            uri, tag = name_parts
        else:
            uri = None
            tag = name
        
        # Template/custom tag
        if uri == self.TEMPLATE_NS:

            if tag in ("ready", "binding"):
                is_content = False
                is_new = False
                source.write("@%s.when_%s" % (parent_id, tag))
                source.write("def _handler():")
                source.indent()
                frame.close_actions.append(source.unindent)

            elif tag == "with":
                with_element = attributes.pop(self.TEMPLATE_NS + ">element")

                if not with_element:
                    raise ParseError(
                        "'with' directive without an 'element' attribute"
                    )

                is_new = False
                frame.element = with_element

            elif tag == "new":
                
                element_factory = attributes.pop(self.TEMPLATE_NS + ">element")

                if not element_factory:
                    raise ParseError(
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
       
        # Document root
        if not self.__root_element_found:
            
            self.__root_element_found = True

            frame.source_block = source = SourceCodeWriter()
            self.__source_blocks.append(source)

            base_name = elem_class_name
            frame.element = "self"
            
            source.write()
            source.write("class %s(%s):" % (self.class_name, base_name))
            source.write()
            source.indent()

            source.write("def __init__(self, *args, **kwargs):")
            source.indent()
            source.write("%s.__init__(self, *args, **kwargs)" % base_name)

            if elem_tag is not default:
                source.write("self.tag = %r" % elem_tag)

            self._handle_attributes("self", attributes)
            source.unindent()
            source.write()

            source.write("def _build(self):")
            source.indent()
            source.write("%s._build(self)" % elem_class_name)
        
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
            def_identifier = \
                attributes.pop(self.TEMPLATE_NS + ">def", None)

            # Get the generated and user defined identifiers for the element
            if is_new:
                id = "_e" + str(self.__element_id)
                self.__element_id += 1
                frame.element = id

                # Instantiation
                if def_identifier is None:

                    source.write()
            
                    # If the element is being created through the 'new'
                    # directive, the user will have provided an expression to
                    # produce the new element. Otherwise, determine the
                    # instantiation expression for the element as follows:
                    if element_factory is None:
                        
                        # Elements with a user defined name get their own
                        # factory method, which will be invoked to obtain a new
                        # instance
                        if identifier:
                            element_factory = "self.create_%s()" % identifier

                        # In any other case, the element is instantiated by 
                        # invoking its class without arguments
                        else:
                            element_factory = "%s()" % elem_class_name

                    source.write("%s = %s" % (id, element_factory))

                    # Use the user defined name to bind elements to their
                    # parents
                    if identifier is not None and iter_expr is None:
                        source.write("self.%s = %s" % (identifier, id))

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
                else:
                    source.write("%s.append(%s)" % (parent_id, id))

            # Elements with a user defined identifier get their own factory
            # method, so that subclasses and containers can extend or override
            # it as needed
            if identifier or def_identifier:

                # Declaration
                frame.source_block = source = SourceCodeWriter(1)
                self.__source_blocks.append(source)                
                
                args = attributes.pop(self.TEMPLATE_NS + ">args", None)
                source.write(
                    "def create_%s(self%s):"
                    % (
                        identifier or def_identifier,
                        ", " + args if args else ""
                    )
                )
                source.indent()

                # Instantiation
                source.write("%s = %s()" % (id, elem_class_name))
                source.write(
                    "%s.add_class(%s)"
                    % (id, repr(identifier or def_identifier))
                )
                
                @frame.closing
                def return_element():
                    source.write("return %s" % id)
                    source.unindent()
                
            # Attributes and properties
            if elem_tag is not default:
                source.write("%s.tag = %r" % (id, elem_tag))

            self._handle_attributes(id, attributes)
    
    def EndElementHandler(self, name):
        self._pop()
    
    def CharacterDataHandler(self, data):

        data = data.strip()

        if data:
            parent_id = self._get_current_element()
            
            for chunk, expr_type in self._parse_data(data):

                source = self.__stack[-1].source_block

                if expr_type == LITERAL:
                    source.write('%s.append(%r)' % (parent_id, chunk))

                elif expr_type == EXPRESSION:
                    source.write('%s.append(unicode(%s))' \
                        % (parent_id, chunk))
                
                elif expr_type == PLACEHOLDER:
                    source.write(
                        '%s.append(' % parent_id,
                        self.add_class_reference(
                            "cocktail.html.PlaceHolder"
                        ),
                        '(lambda: %s))' % chunk
                    )

    def DefaultHandler(self, data):        
        if data.startswith("<?py") and data[4] in (" \n\r\t"):
            data = data[5:-2]
            lines = data.split("\n")
            
            for line in lines:
                if line.strip():
                    indent_str = WHITESPACE_EXPR.match(line).group(0)
                    break
            indent_end = len(indent_str)
            source = self.__stack[-1].source_block

            # Add a consistent reference to the currently processed element
            if self.__root_element_found \
            and not self.__context_is_current:
                source.write("element = " + self._get_current_element())
                self.__context_is_current = True

            for i, line in enumerate(lines):
                if not line.startswith(indent_str) and line.strip():
                    raise ParseError(
                        "Inconsistent indentation on code block (line %d)"
                        % (self.__parser.CurrentLineNumber + i)
                    )
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
                        raise ParseError("'else' directive must be empty")
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
            
            value_source = " + ".join(chunks)

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

