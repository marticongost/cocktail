#-*- coding: utf-8 -*-
u"""
Definition of multi-language string catalogs.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from .translation import (
    translations,
    language_context,
    get_language,
    set_language,
    require_language,
    get_root_language,
    language_has_fallback,
    iter_language_chain,
    iter_derived_languages,
    descend_language_tree,
    fallback_languages_context,
    clear_fallback_languages,
    set_fallback_languages,
    add_fallback_language,
    NoActiveLanguageError
)
from .wordprocessing import words
from . import directionality

translations.load_bundle("cocktail.translations.package")

from .datetimetranslations import (
    DATE_STYLE_NUMBERS,
    DATE_STYLE_ABBR,
    DATE_STYLE_TEXT,
    month_name,
    month_abbr,
    weekday_name,
    weekday_abbr,
    translate_date_range
)
from .localetranslations import translate_locale, translate_locale_component
from .currencytranslations import (
    translate_currency,
    get_currency_sign,
    format_money
)

