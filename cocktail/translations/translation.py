#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from threading import local
from contextlib import contextmanager
from warnings import warn
from cocktail.modeling import DictWrapper
from cocktail.pkgutils import get_full_name

_thread_data = local()


class UndefinedTranslation(object):

    def __nonzero__(self):
        return False

    def __str__(self):
        return "Undefined translation"

undefined = UndefinedTranslation()


@contextmanager
def language_context(language):

    prev_language = get_language()

    try:
        set_language(language)
        yield prev_language
    finally:
        set_language(prev_language)

def get_language():
    return getattr(_thread_data, "language", None)

def set_language(language):
    setattr(_thread_data, "language", language)


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
                translation = Translation()
                self.__translations[language] = translation
            
            translation[obj] = string

    def __call__(self, obj,
        language = None,
        default = undefined,
        chain = undefined,
        **kwargs):
        
        value = undefined

        if language is None:
            language = get_language()

        # Translation method
        translation_method = getattr(obj, "__translate__", None)

        if translation_method:
            value = translation_method(language, **kwargs)
        
        # Translation key
        if value is undefined:
            translation = self.__translations.get(language, None)
            if translation is not None:
                value = translation(obj, **kwargs)

        # Per-type translation
        if value is undefined \
        and not isinstance(obj, basestring) \
        and hasattr(obj.__class__, "mro"):

            for cls in obj.__class__.mro():
                try:
                    type_key = get_full_name(cls) + "-instance"
                except:
                    type_key = cls.__name__ + "-instance"
                        
                value = self(type_key, language, instance = obj, **kwargs)
                
                if value is not undefined:
                    break
        
        # Custom translation chain
        if value is undefined and chain is not undefined:
            value = self(chain, language, default, **kwargs)

        # Object specific translation chain
        if value is undefined:
            object_chain = getattr(obj, "translation_chain", undefined)
            if object_chain is not undefined:
                value = self(object_chain, language, default, **kwargs)

        # Explicit default
        if value is undefined and default is not undefined:
            value = unicode(default)

        return value

translations = TranslationsRepository()

def translate(*args, **kwargs):
    warn(
        "translate() is deprecated, use translations() instead",
        DeprecationWarning,
        stacklevel = 2,
    )
    return translations(*args, **kwargs)


class Translation(DictWrapper):

    language = None

    def __init__(self):
        self.__strings = {}
        DictWrapper.__init__(self, self.__strings)

    def __setitem__(self, obj, string):
        self.__strings[obj] = string

    def __call__(self, obj, **kwargs):
        
        value = self.__strings.get(obj, undefined)
    
        if value is not undefined:

            # Custom python expression
            if callable(value):
                value = value(**kwargs)

            # String formatting
            elif kwargs:
                value = value % kwargs

        return value

