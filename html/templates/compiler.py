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

    TEMPLATE_NS = "http://www.whads.com/ns/cocktail/templates"
    XHTML_NS = "http://www.w3.org/1999/xhtml"

    def __init__(self, xml = None, class_name = "Template"):
        self.class_name = class_name
        self.__classes = {}
        self.__class_names = set()
        self.__element_id = 0
        self.__stack = []
        self.__root_element_found = False
        self.__parser = expat.ParserCreate(namespace_separator = ">")
        self.__source = SourceCodeWriter()
        self.__context_is_current = False
        
        for key in dir(self):
            if key.endswith("Handler"):
                setattr(self.__parser, key, getattr(self, key))

        if xml is not None:
            self.compile(xml)            

    def compile(self, xml):        
        self.__parser.Parse(xml, True)
        self.__source.write("\n")

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
#        print "-" * 80
#        print self.source
#        print "-" * 80
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
    
    def _push(self):
        element = Frame()
        self.__stack.append(element)
        self.__context_is_current = False
        return element

    def _pop(self):
        self.__context_is_current = False
        return self.__stack.pop()   

    def StartElementHandler(self, name, attributes):
        
        frame = self._push()
        source = self.__source
        name_parts = name.split(">")
        is_content = True
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

                is_content = False
                frame.element = with_element

            elif tag == "block":
                elem_class_fullname = "cocktail.html.Element"
                elem_tag = None
            else:
                elem_class_fullname = tag
                elem_tag = default
        else:            
            elem_class_fullname = "cocktail.html.Element"
            elem_tag = tag

        if is_content:
            elem_class_name = self.add_class_reference(elem_class_fullname)

        self._handle_conditions(attributes)
       
        # Document root
        if not self.__root_element_found:
            
            self.__root_element_found = True
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

            # Generated element id
            id = "_e" + str(self.__element_id)
            self.__element_id += 1
            frame.element = id
             
            # Instantiation
            source.write()
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
                source.write("%s.add_class(%s)" % (id, repr(name)))

            # Attributes and properties
            if elem_tag is not default:
                source.write("%s.tag = %r" % (id, elem_tag))

            self._handle_attributes(id, attributes)
    
    def EndElementHandler(self, name):
        
        frame = self._pop()
        
        for close_action in frame.close_actions:
            close_action()
    
    def CharacterDataHandler(self, data):

        data = data.strip()

        if data:
            parent_id = self._get_current_element()
            
            for chunk, expr_type in self._parse_data(data):

                if expr_type == LITERAL:
                    self.__source.write('%s.append(%r)' % (parent_id, chunk))

                elif expr_type == EXPRESSION:
                    self.__source.write('%s.append(unicode(%s))' \
                        % (parent_id, chunk))
                
                elif expr_type == PLACEHOLDER:
                    self.__source.write(
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
            indent_end = len(indent_str)
            write = self.__source.write

            # Add a consistent reference to the currently processed element
            if self.__root_element_found \
            and not self.__context_is_current:
                write("element = " + self._get_current_element())
                self.__context_is_current = True

            for i, line in enumerate(lines):
                if not line.startswith(indent_str) and line.strip():
                    raise ParseError(
                        "Inconsistent indentation on code block (line %d)"
                        % (self.__parser.CurrentLineNumber + i)
                    )
                line = line[indent_end:]
                write(line)

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
            self.__source.write(condition_statement)
            self.__source.indent()
            self.__stack[-1].close_actions.append(self.__source.unindent)

    def _handle_attributes(self, id, attributes):
        
        source = self.__source
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


if __name__ == "__main__":
    source = file("/home/marti/Projectes/sitebasis/src/sitebasis/views/Installer.xml").read()
    TemplateCompiler(source, "Installer").template_class

