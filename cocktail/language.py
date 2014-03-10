#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from warnings import warn
from cocktail.translations import get_language as get_content_language
from cocktail.translations import set_language as set_content_language
from cocktail.translations import require_language as require_content_language
from cocktail.translations import language_context as content_language_context
from cocktail.translations import NoActiveLanguageError

warn(
    "The cocktail.language module has been deprecated in favor of "
    "cocktail.translations",
    DeprecationWarning,
    stacklevel = 2
)

