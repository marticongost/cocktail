#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from abc import ABCMeta, abstractmethod
from warnings import warn
import re
import collections
from Stemmer import Stemmer
from cocktail.stringutils import normalize, create_normalization_map
from cocktail.translations.translation import iter_language_chain


class PerLocaleWordProcessing(dict):

    def get_processor_for_locale(self, locale):

        if locale:
            for locale in iter_language_chain(locale):
                processor = self.get(locale)
                if processor is not None:
                    return processor

        return self.get(None)

    def require_processor_for_locale(self, locale):
        processor = self.get_processor_for_locale(locale)
        if processor is None:
            raise ValueError(
                "No word processor defined for locale %r" % locale
            )
        return processor

    def normalize(self, text, locale = None, preserve_patterns = False):
        return self.require_processor_for_locale(locale).normalize(
            text,
            preserve_patterns = preserve_patterns
        )

    def split(self, text, locale = None, preserve_patterns = False):
        return self.require_processor_for_locale(locale).split(
            text,
            preserve_patterns = preserve_patterns
        )

    def get_stem(self, word, locale = None, preserve_patterns = False):
        return self.require_processor_for_locale(locale).get_stem(
            word,
            preserve_patterns = preserve_patterns
        )

    def get_stems(self, text, locale = None, preserve_patterns = False):
        return self.require_processor_for_locale(locale).get_stems(
            text,
            preserve_patterns = preserve_patterns
        )

    def get_unique_stems(self, text, locale = None, preserve_patterns = False):
        return self.require_processor_for_locale(locale).get_unique_stems(
            text,
            preserve_patterns = preserve_patterns
        )

    def iter_stems(self, text, locale = None, preserve_patterns = False):
        return self.require_processor_for_locale(locale).iter_stems(
            text,
            preserve_patterns = preserve_patterns
        )


class WordProcessor(object):

    __metaclass__ = ABCMeta

    non_word_regexp = re.compile(r"\W+", re.UNICODE)
    non_pattern_regexp = re.compile(r"[^\w*?]+", re.UNICODE)

    normalization = create_normalization_map()
    pattern_normalization = create_normalization_map(preserved_chars = "*?")

    def normalize(self, text, preserve_patterns = False):
        return normalize(
            text,
            normalization_map =
                self.pattern_normalization
                    if preserve_patterns
                    else self.normalization
        )

    def split(self, text, preserve_patterns = False):
        if preserve_patterns:
            return [
                word
                for word in self.non_pattern_regexp.split(text)
                if word
            ]
        else:
            return [
                word
                for word in self.non_word_regexp.split(text)
                if word
            ]

    @abstractmethod
    def get_stem(self, word, preserve_patterns = False):
        pass

    def get_stems(self, text, preserve_patterns = False):
        if isinstance(text, basestring):
            return list(
                self.iter_stems(
                    text,
                    preserve_patterns = preserve_patterns
                )
            )
        elif isinstance(text, collections.Iterable):
            stems = []
            for chunk in text:
                stems.extend(
                    self.iter_stems(
                        chunk,
                        preserve_patterns = preserve_patterns
                    )
                )
            return stems
        else:
            raise TypeError(
                "WordProcessor.get_stems() expected a string or an iterable "
                "sequence, got %s instead" % type(text)
            )

    def get_unique_stems(self, text, preserve_patterns = False):
        if isinstance(text, basestring):
            return set(
                self.iter_stems(
                    text,
                    preserve_patterns = preserve_patterns
                )
            )
        elif isinstance(text, collections.Iterable):
            stems = set()
            for chunk in text:
                stems.update(
                    self.iter_stems(
                        chunk,
                        preserve_patterns = preserve_patterns
                    )
                )
            return stems
        else:
            raise TypeError(
                "WordProcessor.get_stems() expected a string or an iterable, "
                "got %s instead" % type(text)
            )

    def iter_stems(self, text, preserve_patterns = False):
        text = self.normalize(text, preserve_patterns = preserve_patterns)
        return (
            self.get_stem(word, preserve_patterns = preserve_patterns)
            for word in self.split(text, preserve_patterns = preserve_patterns)
        )


class GenericWordProcessor(WordProcessor):

    def get_stem(self, word, preserve_patterns = False):
        return word


class LocaleWordProcessor(WordProcessor):

    def __init__(self, stemmer):
        self.stemmer = stemmer

    def get_stem(self, word, preserve_patterns = False):
        return self.stemmer.stemWord(word)


words = PerLocaleWordProcessing()
words[None] = GenericWordProcessor()

for language in (
    "ca",
    "da",
    "nl",
    "en",
    "fi",
    "fr",
    "de",
    "hu",
    "it",
    "no",
    "pt",
    "ro",
    "ru",
    "es",
    "sv",
    "tr"
):
    try:
        stemmer = Stemmer(language)
    except:
        warn("Couldn't create stemmer for language %r" % language)
    else:
        words[language] = LocaleWordProcessor(stemmer)

