#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .translation import translations

translations.load_bundle("cocktail.translations.currencytranslations")

def translate_currency(currency, language = None):
    return translations("cocktail.currencies." + currency, language = language)

def get_currency_sign(currency):
    return translations("cocktail.currencies.%s.sign" % currency)

def format_money(
    amount,
    currency,
    format = "sign",
    language = None
):
    amount_label = translations(amount, language = language)

    if format == "sign":
        currency_label = get_currency_sign(currency)
        if not currency_label:
            format = "iso"
            currency_label = currency
    elif format == "iso":
        currency_label = currency
    else:
        raise ValueError(
            "Invalid format: expected one of 'sign' or 'iso', got %r instead"
            % format
        )

    return translations(
        "cocktail.money_format",
        language = language,
        amount = amount_label,
        currency = currency_label
    )

