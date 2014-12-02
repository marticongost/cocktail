#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail.translations import translations
from cocktail.schema.member import Member


class Boolean(Member):
    type = bool

    def translate_value(self, value, language = None, **kwargs):
        if value is None:
            return u""
        else:
            return translations(value, language, **kwargs)

