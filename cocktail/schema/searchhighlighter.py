#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import fnmatch
import re
from cocktail.translations import words, get_language
from .textextractor import TextExtractor


class SearchHighlighter(object):

    context_radius = 8
    ellipsis = " ... "
    word_expr = re.compile(r"\w+", re.UNICODE)

    def __init__(self,
        query_text,
        languages,
        emphasis = "*%s*",
        context_radius = None,
        ellipsis = None,
        match_mode = "whole_word"
    ):
        self.match_mode = match_mode

        if isinstance(emphasis, basestring):
            self.__emphasize = lambda text: emphasis % text
        elif callable(emphasis):
            self.__emphasize = emphasis
        else:
            raise TypeError(
                "SearchHighlighter constructor received an invalid value for "
                "its 'emphasis' parameter: expected a formatting string or a "
                "callable with a single parameter, got %r instead." % emphasis
            )

        if languages is None:
            self.__languages = (None, get_language())
        else:
            self.__languages = languages

        self.__query_stems = set()

        for language in self.__languages:
            stems = words.iter_stems(
                query_text,
                language,
                preserve_patterns = (match_mode == "pattern")
            )
            if match_mode == "prefix":
                stems = [stem + u"*" for stem in stems]
            self.__query_stems.update(stems)

        if context_radius is not None:
            self.context_radius = context_radius

        if ellipsis is not None:
            self.ellipsis = ellipsis

    def emphasize(self, text):
        return self.__emphasize(text)

    def highlight(self, obj):

        output = []

        def word_matches_query(word):
            for language in self.__languages:
                for stem in words.iter_stems(word, language):
                    if self.match_mode == "whole_word":
                        if stem in self.__query_stems:
                            return True
                    else:
                        for pattern in self.__query_stems:
                            if fnmatch.fnmatch(stem, pattern):
                                return True
            return False

        extractor = TextExtractor(self.__languages)
        extractor.extract(obj.__class__, obj)

        for node in extractor.nodes:

            if not self.should_include(node):
                continue

            pos = 0
            queue = []
            trailing_context = 0
            text = u" ".join(node.text)
            ellipsis = False

            # Separate the output of different nodes
            if output:
                text = u" " + text
        
            while True:
                match = self.word_expr.search(text, pos)
                if match is None:
                    break

                word_start, word_end = match.span()
                separator = text[pos:word_start]
                word = match.group(0)
                matches = word_matches_query(word)

                if matches:
                    if ellipsis:
                        output.append(self.ellipsis)
                        ellipsis = False
                    output.extend(queue)
                    output.append(separator + self.emphasize(word))
                    queue = []
                    trailing_context = self.context_radius
                elif trailing_context:
                    output.append(separator + word)
                    trailing_context -= 1
                else:
                    if len(queue) == self.context_radius:
                        queue.pop(0)
                        ellipsis = True
                    queue.append(separator + word)

                pos = word_end

        return u"".join(output)

    def should_include(self, node):
        return True

