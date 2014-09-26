#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.styled import styled
from collections import namedtuple
from cocktail.translations import get_language
from cocktail.schema.schema import Schema


class TextExtractor(object):

    verbose = False

    def __init__(self, languages = None):

        if languages is None:
            current_language = get_language()
            if current_language is None:
                languages = (None,)
            else:
                languages = (None, current_language) 

        self.__languages = languages
        self.__stack = []
        self.__visited = set()
        self.__nodes = []
 
    @property
    def languages(self):
        return self.__languages

    @property
    def stack(self):
        return self.__stack

    @property
    def nodes(self):
        return self.__nodes

    @property
    def current(self):
        try:
            return self.__stack[-1]
        except IndexError:
            return None

    def extract(self, member, value, language = None):

        if value is None:
            return False

        if self.verbose:
            print (" " * 4 * len(self.__stack)) + "Extracting",
            print styled(member, style = "bold"),
            print "from",
            print styled(value, style = "bold"),

            if language:
                print "in language", styled(language, style = "bold")
            else:
                print

        is_object = issubclass(type(value), Schema)

        if is_object:
            if value in self.__visited:
                return False
            else:
                self.__visited.add(value)

        node = TextExtractorNode(member, language, value, [])
        self.__stack.append(node)

        try:
            member.extract_searchable_text(self)
        finally:
            self.__stack.pop(-1)

        return True

    def feed(self, text):

        try:
            node = self.__stack[-1]
        except IndexError:
            raise ValueError("The text extraction stack is empty")

        # Make sure we aren't fed crap
        if not isinstance(text, basestring):
            raise TypeError(
                "Non string value %r produced during text extraction. \n"
                "Extraction stack: %r\n"
                "Check the implementation of the extract_searchable_text() "
                "method of the involved objects."
                % (text, self.__stack)
            )

        # Ignore strings that aren't or can't be converted to unicode
        if isinstance(text, str):
            try:
                text = unicode(text)
            except UnicodeDecodeError:
                return

        if not node.text:
            self.__nodes.append(node)

        node.text.append(text)

        if self.verbose:
            print (" " * 4 * len(self.__stack)) + "Feeding",
            print styled(text, "brown")

    def __unicode__(self):
        return u" ".join(
            u" ".join(chunk for chunk in node.text)
            for node in self.__nodes
        )


TextExtractorNode = namedtuple("TextExtractorNode", [
    "member",
    "language",
    "value",
    "text"
])

