#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.styled import styled
from collections import namedtuple
from cocktail.translations import (
    get_language,
    descend_language_tree,
    iter_language_chain
)
from cocktail.schema.schema import Schema


class TextExtractor(object):

    verbose = False

    def __init__(self,
        languages = None,
        include_derived_languages = False,
        verbose = None
    ):
        self.__languages = languages
        self.__include_derived_languages = include_derived_languages
        self.__stack = []
        self.__visited = set()
        self.__nodes = []

        if languages is None:
            self.__accepted_languages = None
        elif include_derived_languages:
            self.__accepted_languages = set()
            for language in languages:
                self.__accepted_languages.update(descend_language_tree(language))
        else:
            self.__accepted_languages = set(languages)

        if verbose is not None:
            self.verbose = verbose

    def iter_node_languages(self):

        if not self.__stack:
            raise ValueError("The text extraction stack is empty")

        if self.__stack[-1].member.translated:
            return self.iter_object_languages()
        else:
            return self.iter_extractor_languages()

    def iter_extractor_languages(self):
        if self.__languages:
            for language in self.__languages:
                if self.__include_derived_languages:
                    for derived_language in descend_language_tree(
                        language,
                        include_self = True
                    ):
                        yield derived_language
                else:
                    yield language

    def iter_object_languages(self):

        for node in reversed(self.__stack):
            if isinstance(node.value.__class__, Schema):
                obj = node.value
                break
        else:
            raise ValueError("The text extraction stack is empty")

        if obj.__class__.translated:
            for language in obj.iter_translations(
                include_derived = self.__include_derived_languages,
                languages = self.__languages
            ):
                yield language
        else:
            yield None

    @property
    def languages(self):
        return self.__languages

    @property
    def include_derived_languages(self):
        return self.__include_derived_languages

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
            print((" " * 4 * len(self.__stack)) + "Extracting", end=' ')
            print(styled(member, style = "bold"), end=' ')
            print("from", end=' ')
            print(styled(value, style = "bold"), end=' ')

            if language:
                print("in language", styled(language, style = "bold"))
            else:
                print()

        is_object = isinstance(type(value), Schema)

        if is_object:
            if value in self.__visited:
                return False
            else:
                self.__visited.add(value)

        node = TextExtractorNode(
            member,
            language,
            value,
            [],
            self.__stack[-1] if self.__stack else None
        )
        self.__stack.append(node)

        try:
            member.extract_searchable_text(self)
        finally:
            self.__stack.pop(-1)

        return True

    def feed(self, text):

        if (
            self.__accepted_languages is not None
            and self.current.language not in self.__accepted_languages
        ):
            return False

        try:
            node = self.__stack[-1]
        except IndexError:
            raise ValueError("The text extraction stack is empty")

        # Make sure we aren't fed crap
        if not isinstance(text, str):
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
                text = str(text)
            except UnicodeDecodeError:
                return False

        if not node.text:
            self.__nodes.append(node)

        node.text.append(text)

        if self.verbose:
            print((" " * 4 * len(self.__stack)) + "Feeding", end=' ')
            print(styled(text, "brown"))

        return True

    def __unicode__(self):
        return " ".join(
            " ".join(chunk for chunk in node.text)
            for node in self.__nodes
        )

    def get_text_by_language(self):

        buffers = {}

        for node in self.__nodes:
            lang_buffer = buffers.get(node.language)
            if lang_buffer is None:
                buffers[node.language] = lang_buffer = []
            lang_buffer.extend(node.text)

        return dict(
            (lang, " ".join(buffer))
            for lang, buffer in buffers.items()
        )


TextExtractorNode = namedtuple("TextExtractorNode", [
    "member",
    "language",
    "value",
    "text",
    "parent"
])

