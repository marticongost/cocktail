#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from __future__ import with_statement
from threading import local
from contextlib import contextmanager
from cocktail.modeling import (
    getter,
    DictWrapper,
    ListWrapper,
    OrderedSet
)
from cocktail.pkgutils import get_full_name

_thread_data = local()

@contextmanager
def language_context(language):

    if language:
        prev_language = get_language()
        set_language(language)

    try:
        yield None
    finally:
        if language:
            set_language(prev_language)

def get_language():
    return getattr(_thread_data, "language", None)

def set_language(language):
    setattr(_thread_data, "language", language)

def require_language(language = None):
    if not language:
        language = get_language()

    if not language:
        raise NoActiveLanguageError()

    return language

def iter_language_chain(language = None, include_self = True):
    language = require_language(language)
    if include_self:
        yield language
    fallback_map = getattr(_thread_data, "fallback", None)
    if fallback_map is not None:
        base_languages = fallback_map.get(language)
        if base_languages is not None:
            for base in base_languages:
                for ancestor in iter_language_chain(base):
                    yield ancestor

def descend_language_tree(language = None, include_self = True):
    language = require_language(language)
    if include_self:
        yield language
    derived_map = getattr(_thread_data, "derived", None)
    if derived_map is not None:
        derived_languages = derived_map.get(language)
        if derived_languages is not None:
            for derived in derived_languages:
                for descendant in descend_language_tree(derived):
                    yield descendant

def iter_derived_languages(language):
    derived_map = getattr(_thread_data, "derived", None)
    if derived_map is not None:
        derived_languages = derived_map.get(language)
        if derived_languages is not None:
            for derived in derived_languages:
                yield derived

@contextmanager
def fallback_languages_context(fallback_chains):
    prev_fallback = getattr(_thread_data, "fallback", None)
    prev_derived = getattr(_thread_data, "derived", None)
    try:
        _thread_data.fallback = {}
        _thread_data.derived = {}
        for language, chain in fallback_chains.iteritems():
            set_fallback_languages(language, chain)
        yield None
    finally:
        _thread_data.fallback = prev_fallback
        _thread_data.derived = prev_derived

def set_fallback_languages(language, fallback_languages):

    fallback_map = getattr(_thread_data, "fallback", None)
    if fallback_map is None:
        _thread_data.fallback = fallback_map = {}

    derived_map = getattr(_thread_data, "derived", None)
    if derived_map is None:
        _thread_data.derived = derived_map = {}
    else:
        prev_fallback_languages = fallback_map.get(language)
        if prev_fallback_languages:
            for prev_fallback_language in prev_fallback_languages:
                derived_languages = derived_map.get(prev_fallback_language)
                if derived_languages is not None:
                    derived_languages.remove(language)

    fallback_map[language] = OrderedSet(fallback_languages)

    for fallback_language in fallback_languages:
        derived_languages = derived_map.get(fallback_language)
        if derived_languages is None:
            derived_map[fallback_language] = OrderedSet([language])
        else:
            derived_languages.append(language)

def add_fallback_language(language, fallback_language):
    fallback_languages = []
    language_chain = iter_language_chain(language)
    language_chain.next()
    fallback_languages.extend(language_chain)
    fallback_languages.append(fallback_language)
    set_fallback_languages(language, fallback_languages)

def clear_fallback_languages():
    _thread_data.fallback = {}
    _thread_data.derived = {}


class TranslationsRepository(DictWrapper):

    def __init__(self):
        self.__translations = {}
        DictWrapper.__init__(self, self.__translations)

    def __setitem__(self, language, translation):
        self.__translations[language] = translation
        translation.language = language

    def define(self, obj, **strings):

        for language, string in strings.iteritems():
            translation = self.__translations.get(language)

            if translation is None:
                translation = Translation(language)
                self.__translations[language] = translation

            translation[obj] = string

    def clear_key(self, obj):
        """Remove all translations of the given key for all languages."""
        for trans in self.__translations.itervalues():
            try:
                del trans[obj]
            except KeyError:
                pass

    def copy_key(self, source, dest, overwrite = True):
        """Copy the translated strings of the given key into another key."""
        for trans in self.__translations.itervalues():
            string = trans(source)
            if string and (overwrite or not trans(dest)):
                trans[dest] = string

    def __call__(self, obj,
        language = None,
        default = "",
        chain = None,
        **kwargs):

        language = require_language(language)

        # Translation method
        translation_method = getattr(obj, "__translate__", None)

        if translation_method:
            for lang in iter_language_chain(language):
                value = translation_method(lang, **kwargs)
                if value:
                    return value

        # Translation key
        for lang in iter_language_chain(language):
            translation = self.__translations.get(lang, None)
            if translation is not None:
                value = translation(obj, **kwargs)
                if value:
                    return value

        # Per-type translation
        if not isinstance(obj, basestring) and hasattr(obj.__class__, "mro"):

            for cls in obj.__class__.mro():
                try:
                    type_key = get_full_name(cls) + "-instance"
                except:
                    type_key = cls.__name__ + "-instance"

                for lang in iter_language_chain(language):
                    value = self(type_key, lang, instance = obj, **kwargs)
                    if value:
                        return value

        # Custom translation chain
        if chain is not None:
            value = self(chain, language, default, **kwargs)
            if value:
                return value

        # Object specific translation chain
        object_chain = getattr(obj, "translation_chain", None)
        if object_chain is not None:
            value = self(object_chain, language, default, **kwargs)
            if value:
                return value

        # Explicit default
        return unicode(default) if default != "" else ""

translations = TranslationsRepository()


class Translation(DictWrapper):

    language = None

    def __init__(self, language):
        self.__language = language
        self.__strings = {}
        DictWrapper.__init__(self, self.__strings)

    @getter
    def language(self):
        return self.__language

    def __setitem__(self, obj, string):
        self.__strings[obj] = string

    def __delitem__(self, obj):
        del self.__strings[obj]

    def __call__(self, obj, **kwargs):

        try:
            value = self.__strings.get(obj, "")
        except TypeError:
            return ""

        if value:

            # Custom python expression
            if callable(value):
                with language_context(self.__language):
                    value = value(**kwargs)

            # String formatting
            elif kwargs:
                value = value % kwargs

        return value


class NoActiveLanguageError(Exception):
    """Raised when trying to access a translated string without specifying
    a language.
    """

