#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from contextlib import contextmanager
from cocktail.stringutils import normalize_indentation


class SourceCodeWriter(object):

    def __init__(self, indentation = 0):
        self.__content = []
        self.indentation = indentation
        self.line_separator = u"\n"
        self.indent_str = " " * 4

    def __unicode__(self):
        return self.line_separator.join(
            unicode(content)
            for content in self.__content
        )

    def write(self, *text):
        indent_str = self.indent_str * self.indentation
        code = normalize_indentation(u"".join(text))
        lines = code.split(self.line_separator)
        for line in lines:
            self.__content.append(indent_str + line)

    def write_lines(self, *lines):
        for line in lines:
            self.write(line)

    def nest(self, indent = 0):
        child = self.__class__(self.indentation + indent)
        self.__content.append(child)
        return child

    def append(self, content):
        self.__content.append(content)

    def indent(self):
        self.indentation += 1

    def unindent(self):
        self.indentation -= 1

    @contextmanager
    def indented_block(self, opening = None, closure = None):
        if opening:
            self.write(opening)
        self.indentation += 1
        try:
            yield self
        finally:
            self.indentation -= 1
            if closure:
                self.write(closure)

    def braces(self, opening = None, closure = None):

        if opening:
            opening += " {"
        else:
            opening = "{"

        if closure:
            closure = "}" + closure
        else:
            closure = "}"

        return self.indented_block(opening, closure)

    def linejump(self, lines = 1):
        for i in xrange(lines):
            self.write()

    def __iadd__(self, content):
        self.append(content)
        return self

