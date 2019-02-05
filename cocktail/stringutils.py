#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from random import choice
from string import letters, digits
from html.parser import HTMLParser
from html.entities import name2codepoint

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

def create_normalization_map(normalization = None, preserved_chars = None):

    if normalization is None:
        normalization = {
            "a": "áàäâ",
            "e": "éèëê",
            "i": "íìïî",
            "o": "óòöô",
            "u": "úùüû",
            " ": "'\"\t\n\r(),.:;+-*/\\¡!¿?&|=[]{}~#¬<>"
        }

    if preserved_chars:
        for norm_char, input_chars in list(normalization.items()):
            for preserved_char in preserved_chars:
                input_chars = input_chars.replace(preserved_char, "")
            normalization[norm_char] = input_chars

    return create_translation_map(normalization)

_normalization_map = create_normalization_map()

def normalize(string, normalization_map = None):
    string = string.lower()

    if not isinstance(string, str):
        try:
            string = str(string)
        except:
            return string

    if isinstance(string, str):
        string = string.translate(normalization_map or _normalization_map)
        string = " ".join(string.split())

    return string

def random_string(length, source = letters + digits + "!?.-$#&@*"):
    return "".join(choice(source) for i in range(length))

def normalize_indentation(string):

    indentation = None
    lines = string.split("\n")
    norm_lines = []

    for i, line in enumerate(lines):
        stripped_line = line.lstrip()
        if not indentation and not stripped_line:
            continue
        else:
            if indentation is None:
                indentation = line[:len(line) - len(stripped_line)]
            elif not line.startswith(indentation) and stripped_line:
                raise ValueError(
                    "Indentation error in line %d (%s)"
                    % (i + 1, stripped_line)
                )

            norm_lines.append(line[len(indentation):])

    return "\n".join(norm_lines)


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
            chunk = chunk.replace("\xa0", " ")
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
        return "".join(self.__chunks).strip()

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
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))

        self._push(c)

    def handle_entityref(self, name):
        code_point = name2codepoint.get(name)
        if code_point is not None:
            self._push(chr(code_point))


def html_to_plain_text(html):
    extractor = HTMLPlainTextExtractor()
    extractor.feed(html)
    return extractor.get_text()

_list_regexp = re.compile(r"(^\s*[-*].*$\s*){2,}", re.MULTILINE)
_line_jumps_regexp = re.compile(r"\n{2,}")
_link_regexp = re.compile(r"(\S+)://(\S+)")

def _link_for_match(target):
    def link_repl(match):
        url = "%s://%s" % (match.group(1), match.group(2))
        return '<a href="%s" target="%s">%s</a>' % (url, target, url)
    return link_repl

def _list_for_match(match):

    items = []

    for line in match.group(0).split("\n"):
        line = line.strip().lstrip("-").lstrip("*").lstrip()
        if line:
            items.append("<li>%s</li>" % line)

    return "<ul>" + "".join(items) + "</ul>"

def plain_text_to_html(text, links_target = "_self", paragraphs_policy = "all"):
    text = text.strip()
    text = text.replace("\r\n", "\n")
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = _list_regexp.sub(_list_for_match, text)
    text = _link_regexp.sub(_link_for_match(links_target), text)

    paragraphs_list = _line_jumps_regexp.split(text)

    if paragraphs_policy == "all":
        apply_paragraphs_policy = True
    elif paragraphs_policy == "unless_only_one":
        apply_paragraphs_policy = len(paragraphs_list) > 1
    else:
        raise ValueError(
            "The 'paragraphs_policy' parameter of plain_text_to_html() "
            "should be one of 'all' or 'unless_only_one'; got %s"
            "instead"
            % paragraphs_policy
        )

    if apply_paragraphs_policy:
        text = "".join(
            "<p>%s</p>" % paragraph
            for paragraph in paragraphs_list
        )

    text = text.replace("\n", "<br/>")
    return text

def decapitalize(string):
    if len(string) >= 2 and string[1] == string[1].lower():
        return string[0].lower() + string[1:]
    else:
        return string

