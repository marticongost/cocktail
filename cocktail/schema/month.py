#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import month_name
from cocktail.translations import translations
from cocktail.schema.schemanumbers import Integer


class Month(Integer):

    min = 1
    max = 12

    def translate_value(self, value, language = None, **kwargs):
        if not value:
            return Integer.translate_value(
                self,
                value,
                language = language,
                **kwargs
            )
        else:
            return month_name(value)
