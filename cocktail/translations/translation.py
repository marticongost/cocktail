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
    ListWrapper
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

    def __call__(self, obj,
        language = None,
        default = "",
        chain = None,
        **kwargs):
        
        value = ""
        language = require_language(language)

        # Translation method
        translation_method = getattr(obj, "__translate__", None)

        if translation_method:
            value = translation_method(language, **kwargs)
        
        # Translation key
        if not value:
            translation = self.__translations.get(language, None)
            if translation is not None:
                value = translation(obj, **kwargs)

        # Per-type translation
        if not value \
        and not isinstance(obj, basestring) \
        and hasattr(obj.__class__, "mro"):

            for cls in obj.__class__.mro():
                try:
                    type_key = get_full_name(cls) + "-instance"
                except:
                    type_key = cls.__name__ + "-instance"
                        
                value = self(type_key, language, instance = obj, **kwargs)
                
                if value:
                    break
        
        # Custom translation chain
        if not value and chain is not None:
            value = self(chain, language, default, **kwargs)

        # Object specific translation chain
        if not value:
            object_chain = getattr(obj, "translation_chain", None)
            if object_chain is not None:
                value = self(object_chain, language, default, **kwargs)

        # Explicit default
        if not value and default != "":
            value = unicode(default)

        return value

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

