#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import format_money
from cocktail.schema.schemanumbers import Decimal


class Money(Decimal):

    currency = "EUR"

    def translate_value(
        self,
        value,
        language = None,
        format = "sign",
        decimals = "auto",
        **kwargs):

        if value is None:
            return Decimal.translate_value(self, None, language = language, **kwargs)

        return format_money(
            value,
            self.currency,
            format = format,
            decimals = decimals,
            language = language
        )

