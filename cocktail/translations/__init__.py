#-*- coding: utf-8 -*-
u"""
Definition of multi-language string catalogs.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.translations.translation import (
    TranslationsRepository,
    Translation,
    language_context,
    get_language,
    set_language,
    require_language,
    iter_language_chain,
    iter_derived_languages,
    descend_language_tree,
    fallback_languages_context,
    clear_fallback_languages,
    set_fallback_languages,
    add_fallback_language,
    NoActiveLanguageError,
    translations
)
from cocktail.translations.wordprocessing import words
from cocktail.translations.strings import (
    DATE_STYLE_NUMBERS,
    DATE_STYLE_ABBR,
    DATE_STYLE_TEXT
)

