#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
import re
from xml.parsers import expat
from cocktail.modeling import getter
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

    TEMPLATE_NS = "http://hollowhead.org/ns/cocktail/templates"
    XHTML_NS = "http://www.w3.org/1999/xhtml"

    def __init__(self, xml = None, class_name = "Template"):
        self.class_name = class_name
        self.__classes = {}
        self.__class_names = set()
        self.__element_id = 0
        self.__element_stack = []
        self.__root_element_found = False
        self.__parser = expat.ParserCreate(namespace_separator = ">")
        self.__source = SourceCodeWriter()
        self.__context_is_current = False
        self.__closing_stack = []
        
        for key in dir(self):
            if key.endswith("Handler"):
                setattr(self.__parser, key, getattr(self, key))

        if xml is not None:
            self.compile(xml)

    def compile(self, xml):
        self.__parser.Parse(xml, True)

    @getter
    def source(self):
        
        source = []

        for ref, alias in self.__classes.iteritems():
            pos = ref.rfind(".")
            container = ref[:pos]
            name = ref[pos + 1:]

            if name == alias:
                source.append("from %s import %s" % (container, name))
            else:
                source.append("from %s import %s as %s"
                        % (container, name, alias))

        source.append(unicode(self.__source))
        return u"\n".join(source)

    @getter
    def template_class(self):
        print "-------------------------------------------------------"
        print self.source
        print "-------------------------------------------------------"
        template_scope = {}
        exec self.source in template_scope
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

        return name
    
    def _push_element(self, id):
        self.__context_is_current = False
        self.__element_stack.append(id)

    def _pop_element(self):
        self.__context_is_current = False
        return self.__element_stack.pop()

    def _handle_attributes(self, id, attributes):
        
        source = self.__source
        condition = None
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
            
            if is_template_attrib and name == "if":
                condition = value
            else:
                is_placeholder = False
                chunks = []

                for chunk, expr_type in self._parseData(value):
                    if expr_type == LITERAL:
                        chunks.append(repr(chunk))
                    else:
                        is_placeholder = (expr_type == PLACEHOLDER)
                        chunks.append("unicode(" + chunk + ")")
                
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

        if condition or place_holders:
            source.write("def %s_ready():" % id)
            source.indent()
            
            if place_holders:
                for assignment in place_holders:
                    source.write(assignment)

            if condition:
                source.write("if %s:" % condition)
                source.indent()
                source.write("%s.visible = True" % id)

                def close_condition():
                    source.unindent()
                    source.write("else:")
                    source.indent()
                    source.write("%s.visible = False" % id)
                    source.unindent()
                    source.unindent()
                    source.write(
                        "%s.add_ready_handler(%s_ready)" % (id, id)
                    )

                self.__add_close_action(close_condition)

            else:
                source.unindent()
                source.write(
                    "%s.add_ready_handler(%s_ready)" % (id, id)
                )

    def __add_close_action(self, action):
        self.__closing_stack.append((len(self.__element_stack), action))

    def _parseData(self, data):

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
                    if i != start:
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

    def StartElementHandler(self, name, attributes):
        
        source = self.__source
        name_parts = name.split(">")

        if len(name_parts) > 1:
            uri, tag = name_parts
        else:
            uri = None
            tag = name
        
        # Template/custom tag
        if uri == self.TEMPLATE_NS:
            
            if tag == "block":             
                elem_class_fullname = "cocktail.html.Element"
                elem_tag = None
            else:
                elem_class_fullname = tag
                elem_tag = default
        else:            
            elem_class_fullname = "cocktail.html.Element"
            elem_tag = tag

        elem_class_name = self.add_class_reference(elem_class_fullname)
        
        # Document root
        if not self.__root_element_found:
            
            self.__root_element_found = True
            base_name = elem_class_name
            self._push_element("self")
            
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
            
        # Content
        else:

            # Iteration
            iter_expr = attributes.pop(self.TEMPLATE_NS + ">for", None)
        
            if iter_expr is not None:
                source.write("for " + iter_expr + ":")
                source.indent()
                self.__add_close_action(source.unindent)

            # Element stack
            parent_id = self.__element_stack[-1]
            id = "_e" + str(self.__element_id)
            self.__element_id += 1
            self._push_element(id)
                        
            # Instantiation
            source.write("%s = %s()" % (id, elem_class_name))

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

            name = attributes.pop(self.TEMPLATE_NS + ">id", None)

            # Name
            if name is not None and iter_expr is None:
                source.write("self.%s = %s" % (name, id))

            # Attributes and properties
            if elem_tag is not default:
                source.write("%s.tag = %r" % (id, elem_tag))

            self._handle_attributes(id, attributes)
    
    def EndElementHandler(self, name):
        
        source = self.__source
        current_depth = len(self.__element_stack)
        
        while self.__closing_stack:
            depth, close_action = self.__closing_stack.pop(-1)
            if depth == current_depth:
                close_action()
            else:
                break

        self._pop_element()
    
    def CharacterDataHandler(self, data):

        if self.__element_stack:
            
            data = data.strip()
            
            if data:
                id = self.__element_stack[-1]

                for chunk, expr_type in self._parseData(data):

                    if expr_type == LITERAL:
                        self.__source.write('%s.append(%r)' % (id, chunk))

                    elif expr_type == EXPRESSION:
                        self.__source.write('%s.append(unicode(%s))' \
                            % (id, chunk))
                    
                    elif expr_type == PLACEHOLDER:
                        self.__source.write(
                            '%s.append(' % id,
                            self.add_class_reference(
                                "cocktail.html.PlaceHolder"
                            ),
                            '(lambda: %s))' % chunk
                        )

    def ProcessingInstructionHandler(self, target, data):

        if target == "py":
            lines = data.split("\n")
            indent_str = WHITESPACE_EXPR.match(lines[0]).group(0)
            indent_end = len(indent_str)
            write = self.__source.write

            # Add a consistent reference to the currently processed element
            if self.__root_element_found \
            and not self.__context_is_current:
                write("element = " + self.__element_stack[-1])
                self.__context_is_current = True

            for line in lines:
                if not line.startswith(indent_str):
                    self._raise_parse_error(
                        "Inconsistent indentation on code block (line %s)"
                        % line
                    )
                line = line[indent_end:]
                write(line)

class ParseError(Exception):
    pass

