#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .schemastrings import String
from cocktail.translations import translate_currency, get_currency_sign


class Currency(String):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("enumeration", [
            "EUR",
            "USD",
            "GBP",
            "RUB",
            "TRY",
            "CNY"
        ])
        String.__init__(self, *args, **kwargs)

    def translate_value(
        self,
        value,
        language = None,
        format = "code+label",
        **kwargs
    ):
        translation = None

        if value:

            if format == "sign":
                translation = get_currency_sign(value)
                if not translation:
                    translation = value
            elif format == "code+label":
                translation = translate_currency(value, language = language)
                if translation:
                    translation = u"%s - %s" % (value, translation)
                else:
                    translation = value
            elif format == "code":
                translation = value
            elif format == "label":
                translation = translate_currency(value, language = language)
                if not translation:
                    translation = value
            else:
                raise ValueError(
                    "Invalid currency format: expected one of sign, "
                    "code+label, code or label, got %r instead" % format
                )

        return (
            translation
            or String.translate_value(
                self,
                value,
                language = language,
                **kwargs
            )
        )

