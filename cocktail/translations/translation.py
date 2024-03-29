#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""

from threading import local
from contextlib import contextmanager
from collections import Mapping, defaultdict
from cocktail.pkgutils import resource_filename
from cocktail.styled import styled
from cocktail.events import Event
from cocktail.modeling import (
    DictWrapper,
    ListWrapper,
    OrderedSet
)
from cocktail.pkgutils import get_full_name
from .parser import TranslationsFileParser

_thread_data = local()

@contextmanager
def language_context(language):
    try:
        if language:
            prev_language = get_language()
            set_language(language)
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

def get_root_language(language = None):
    language = require_language(language)
    fallback_map = getattr(_thread_data, "fallback", None)
    if fallback_map:
        while True:
            base_languages = fallback_map.get(language)
            if base_languages is None:
                break
            language = base_languages[0]
    return language

def language_has_fallback(language = None):
    language = require_language(language)
    fallback_map = getattr(_thread_data, "fallback", None)
    return fallback_map is not None and bool(fallback_map.get(language))

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
        for language, chain in fallback_chains.items():
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
    next(language_chain)
    fallback_languages.extend(language_chain)
    fallback_languages.append(fallback_language)
    set_fallback_languages(language, fallback_languages)

def clear_fallback_languages():
    _thread_data.fallback = {}
    _thread_data.derived = {}



class Translations(object):

    bundle_loaded = Event()
    verbose = False

    def __init__(self, *args, **kwargs):
        self.definitions = {}
        self.__loaded_bundles = set()
        self.__bundle_overrides = defaultdict(list)

    def _get_key(self, key, verbose):

        if verbose:
            print((verbose - 1) * 2 * " " + styled("Key", "slate_blue"), key)

        return self.definitions.get(key)

    def define(self, key, value = None, **per_language_values):

        if value is not None and per_language_values:
            raise ValueError(
                "Can't specify both 'value' and 'per_language_values'"
            )

        self.definitions[key] = per_language_values or value

    def set(self, key, language, value):
        per_language_values = self.definitions.get(key)
        if per_language_values is None:
            per_language_values = {}
            self.definitions[key] = per_language_values
        per_language_values[language] = value

    def instances_of(self, cls):

        def decorator(func):
            try:
                class_name = get_full_name(cls)
            except:
                class_name = cls.__name__

            self.definitions[class_name + ".instance"] = func
            return func

        return decorator

    def load_bundle(self, bundle_path, callback = None, reload = False, **kwargs):

        if reload or bundle_path not in self.__loaded_bundles:
            self.__loaded_bundles.add(bundle_path)

            pkg_name, file_name = bundle_path.rsplit(".", 1)
            file_path = resource_filename(pkg_name, file_name + ".strings")

            file_error = None

            try:
                with open(file_path, "r") as bundle_file:
                    parser = TranslationsFileParser(
                        bundle_file,
                        file_path = file_path,
                        **kwargs
                    )
                    for key, language, value in parser:
                        if callback:
                            callback(key, language, value)
                        if language is None:
                            self.definitions[key] = value
                        else:
                            self.set(key, language, value)
            except IOError as e:
                file_error = e
            else:
                self.bundle_loaded(file_path = file_path)

            overrides = self.__bundle_overrides.get(bundle_path)
            if overrides:
                for overrides_path, overrides_kwargs in overrides:
                    self.load_bundle(overrides_path, **kwargs)
            elif file_error:
                raise file_error

    def request_bundle(self, bundle_path, **kwargs):
        try:
            self.load_bundle(bundle_path, **kwargs)
        except IOError:
            pass

    def override_bundle(
        self,
        original_bundle_path,
        overrides_bundle_path,
        **kwargs
    ):
        self.__bundle_overrides[original_bundle_path].append(
            (overrides_bundle_path, kwargs)
        )
        if original_bundle_path in self.__loaded_bundles:
            self.request_bundle(overrides_bundle_path)

    def __iter_class_names(self, cls):

        mro = getattr(cls, "__mro__", None)
        if mro is None:
            mro = (cls,)

        for cls in mro:

            try:
                class_name = get_full_name(cls)
            except:
                class_name = cls.__name__

            yield class_name

    def __call__(
        self,
        obj,
        language = None,
        default = "",
        chain = None,
        **kwargs
    ):
        translation = None

        verbose = kwargs.get("verbose", None)
        if verbose is None:
            if callable(self.verbose):
                verbose = self.verbose(obj, **kwargs)
            else:
                verbose = self.verbose

            verbose = 1 if verbose else 0

        if verbose == 1:
            print(styled("TRANSLATION", "white", "blue"), end=' ')
            print(styled(obj, style = "bold"))

        if verbose:
            kwargs["verbose"] = verbose + 1

        # Look for a explicit definition for the given value
        if isinstance(obj, str):
            translation = self._get_key(obj, verbose)
        else:
            # Translation of class instances
            for class_name in self.__iter_class_names(obj.__class__):
                translation = self._get_key(class_name + ".instance", verbose)
                if translation:
                    break

            # Translation of class references
            if not translation and isinstance(obj, type):
                for class_name in self.__iter_class_names(obj):
                    translation = self(
                        class_name,
                        language = language,
                        **kwargs
                    )
                    if translation:
                        break

        # Resolve the obtained translation
        if translation:
            if callable(translation):
                with language_context(language):

                    if verbose:
                        print(styled("Function", "slate_blue"), end=' ')
                        print(translation)

                    if isinstance(obj, str):
                        translation = translation(**kwargs)
                    else:
                        translation = translation(obj, **kwargs)

            elif isinstance(translation, Mapping):
                definitions = translation
                translation = None
                prev_lang = language or get_language()
                for lang in iter_language_chain(language):
                    translation = definitions.get(lang)
                    if translation:
                        if callable(translation):
                            with language_context(prev_lang):
                                if isinstance(obj, str):
                                    translation = translation(**kwargs)
                                else:
                                    translation = translation(obj, **kwargs)
                            if translation:
                                break
                        else:
                            if kwargs:
                                translation = translation % kwargs
                            break
            elif kwargs:
                translation = translation % kwargs

        # Custom translation chain
        if not translation and chain is not None:
            translation = self(
                chain,
                language = language,
                **kwargs
            )

        if not translation:
            translation = str(default)

        return translation or ""

translations = Translations()


class NoActiveLanguageError(Exception):
    """Raised when trying to access a translated string without specifying
    a language.
    """

