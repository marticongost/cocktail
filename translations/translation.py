#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from threading import local
from contextlib import contextmanager
from cocktail.modeling import DictWrapper
from cocktail.pkgutils import get_full_name

_thread_data = local()
_undefined = object()

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

def translate(obj, language = None, **kwargs):

    translator = getattr(obj, "__translate__", None)

    if language is None:
        language = get_language()

    if translator:
        return translator(language, **kwargs)
    else:
        try:
            return translations(obj, language, **kwargs)
        except KeyError, ex:
            
            if isinstance(obj, basestring):
                raise

            try:
                type_key = get_full_name(type(obj)) + "-instance"
            except:
                type_key = type(obj).__name__ + "-instance"
            
            kwargs["instance"] = obj
            return translations(type_key, language, **kwargs)


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

    def __call__(self, obj, language, **kwargs):
        
        translation = self.__translations.get(language, _undefined)

        if translation is _undefined:
            default = kwargs.get("default", _undefined)
            if default is _undefined:
                raise KeyError("Can't find a translation for %r in language %s"
                            % (obj, language))
            else:
                return unicode(default)
        
        return translation(obj, **kwargs)


class Translation(DictWrapper):

    language = None
    fallback = None

    def __init__(self):
        self.__strings = {}
        DictWrapper.__init__(self, self.__strings)

    def __setitem__(self, obj, string):
        self.__strings[obj] = string

    def _get_with_fallback(self, obj):
        
        string = self.__strings.get(obj, _undefined)

        if string is _undefined and self.fallback:
            for fallback in self.fallback:
                string = fallback._get_with_fallback(obj)
                if string is not _undefined:
                    break

        return string

    def __call__(self, obj, **kwargs):
        
        string = self._get_with_fallback(obj)

        if string is _undefined:
            default = kwargs.get("default", _undefined)
            if default is _undefined:
                raise KeyError("Can't find a translation for %s" % obj)
            else:
                return unicode(default)
        
        # Custom python expression
        if callable(string):
            string = string(**kwargs)

        # String formatting
        elif kwargs:
            string = string % kwargs

        return string


translations = TranslationsRepository()

