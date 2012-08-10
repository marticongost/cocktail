#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail.schema.schemanumbers import Decimal


class Money(Decimal):

    currency = u"€"

    def translate_value(self, value, language = None, **kwargs):
        if value == "" or value is None:
            return ""
        else:
            return translations(value) + " " + self.currency

