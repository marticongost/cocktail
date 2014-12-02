#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""

class SourceCodeWriter(object):

    def __init__(self, indentation = 0):
        self.__lines = []
        self.indentation = indentation
        self.line_separator = u"\n"
        self.indent_str = " " * 4

    def __unicode__(self):
        return self.line_separator.join(self.__lines)

    def write(self, *line):
        indent_str = self.indent_str * self.indentation
        self.__lines.append(indent_str + u"".join(line))

    def indent(self):
        self.indentation += 1

    def unindent(self):
        self.indentation -= 1

