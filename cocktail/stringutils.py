#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from random import choice
from string import letters, digits
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
import BeautifulSoup

normalization_map = {}

def create_translation_map(pairs):

    translation_map = {}

    iteritems = getattr(pairs, "iteritems", None)
    if iteritems is not None:
        pairs = iteritems()

    for repl, chars in pairs:
        for c in chars:
            translation_map[ord(c)] = ord(repl)

    return translation_map

_normalization_map = create_translation_map({
    u"a": u"áàäâ",
    u"e": u"éèëê",
    u"i": u"íìïî",
    u"o": u"óòöô",
    u"u": u"úùüû",
    u" ": u"'\"\t\n\r(),.:;+-*/\\¡!¿?&|=[]{}~#¬<>"
})

def normalize(string):
    string = string.lower()

    if not isinstance(string, unicode):
        try:
            string = unicode(string)
        except:
            return string

    if isinstance(string, unicode):
        string = string.translate(_normalization_map)
        string = u" ".join(string.split())

    return string

def random_string(length, source = letters + digits + "!?.-$#&@*"):
    return "".join(choice(source) for i in xrange(length))


class HTMLPlainTextExtractor(HTMLParser):

    indentation = " " * 2
    bullet = "* "
    excessive_whitespace = re.compile(r"\s\s+")

    def __init__(self):
        HTMLParser.__init__(self)
        self.__depth = 0
        self.__chunks = []

    def _push(self, chunk):
        if chunk:
            if self.__chunks and self.__chunks[-1].endswith("\n"):
                chunk = chunk.lstrip()
                if chunk and self.__depth:
                    chunk = self.indentation * self.__depth + chunk
            if chunk:
                self.__chunks.append(chunk)

    def _break(self, jumps = 1):

        breaks = 0
        content_found = False

        for chunk in reversed(self.__chunks):

            for c in reversed(chunk):
                if c == "\n":
                    breaks += 1
                else:
                    content_found = True
                    break

            if content_found:
                break

        jumps -= breaks
        if jumps > 0:
            self.__chunks.append("\n" * jumps)

    def get_text(self):
        return u"".join(self.__chunks).strip()

    def handle_data(self, data):
        data = data.replace("\n", " ")
        data = self.excessive_whitespace.sub(" ", data)
        self._push(data)

    def handle_starttag(self, tag, attributes):
        if tag == "p":
            self._break(2)
        elif tag == "br":
            self._break(1)
        elif tag == "li":
            self._break(2)
            self._push(self.bullet)
        elif tag in ("ul", "ol"):
            self._break(2)
            self.__depth += 1

    def handle_endtag(self, tag):
        if tag in ("p", "li"):
            self._break(2)
        elif tag in ("ul", "ol"):
            self._break(2)
            self.__depth -= 1

    def handle_charref(self, name):
        if name.startswith('x'):
            c = unichr(int(name[1:], 16))
        else:
            c = unichr(int(name))

        self._push(c)

    def handle_entityref(self, name):
        code_point = name2codepoint.get(name)
        if code_point is not None:
            self._push(unichr(code_point))


def html_to_plain_text(html):
    extractor = HTMLPlainTextExtractor()
    extractor.feed(html)
    return extractor.get_text()


class HTMLCleaner(object):

    content_tags = set([
        "img",
        "hr",
        "br",
        "iframe",
        "object",
        "embed",
        "audio",
        "video"
    ])

    TRIM_LEFT = -1
    TRIM_RIGHT = 1

    start_whitespace = re.compile("^(\\s|&nbsp;|\xa0)+")
    end_whitespace = re.compile("(\\s|&nbsp;|\xa0)+$")

    trim_whitespace = {
        TRIM_LEFT: start_whitespace,
        TRIM_RIGHT: end_whitespace
    }

    def __init__(self, html):
        self.__html_tree = BeautifulSoup.BeautifulSoup(html)
        self.clean_tree(self.__html_tree)
        self.clean_tree(self.__html_tree, trim = self.TRIM_LEFT)
        self.clean_tree(self.__html_tree, trim = self.TRIM_RIGHT)

    def get_clean_html(self):
        return unicode(self.__html_tree)

    def clean_tree(self, node, trim = None):

        if node.__class__ is BeautifulSoup.NavigableString:
            if trim:
                if not self.has_weight(node):
                    node.extract()
                    return True
                else:
                    whitespace = self.trim_whitespace[trim]
                    stripped_text = whitespace.sub("", node)
                    node.replaceWith(stripped_text)

        elif isinstance(node, BeautifulSoup.Tag):
            children = list(node.contents)
            if trim == self.TRIM_RIGHT:
                children.reverse()

            for child in children:
                child_removed = self.clean_tree(child, trim)
                if not child_removed and trim:
                    break

            if node.name == "br":
                if trim:
                    node.extract()
                    return True
            elif (
                node.name not in self.content_tags
                and not any(self.has_weight(child) for child in node.contents)
            ):
                node.extract()
                return True

        return False

    def has_weight(self, node):

        if node.__class__ is BeautifulSoup.NavigableString \
        and not self.start_whitespace.sub("", node):
            return False

        return True


def clean_html(html):
    """Clean an HTML snippet, removing excessive whitespace and empty tags."""
    cleaner = HTMLCleaner(html)
    return cleaner.get_clean_html()

