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
    translations,
    translate,
    ca_apostrophe,
    ca_possessive,
    plural2,
    ca_join,
    ca_either,
    es_join,
    es_either,
    en_join,
    en_either,
    de_join,
    de_either
)
from cocktail.translations import strings

