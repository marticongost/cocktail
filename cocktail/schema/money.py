#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import format_money
from cocktail.schema.schemanumbers import Decimal


class Money(Decimal):

    currency = u"EUR"

    def translate_value(self, value, language = None, format = "sign", **kwargs):

        if value is None:
            return Decimal.translate_value(self, None, language = language, **kwargs)

        return format_money(
            value,
            self.currency,
            format = format,
            language = language
        )

