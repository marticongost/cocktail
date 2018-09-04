#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from decimal import Decimal
from .translation import translations

translations.load_bundle("cocktail.translations.currencytranslations")

currency_precision = {
    "EUR": 2,
    "USD": 2
}

def translate_currency(currency, language = None):
    return translations("cocktail.currencies." + currency, language = language)

def get_currency_sign(currency):
    return translations("cocktail.currencies.%s.sign" % currency)

def format_money(
    amount,
    currency,
    format = "sign",
    decimals = "auto",
    language = None
):
    if decimals == "auto":
        decimals = currency_precision.get(currency, 0)

    if decimals is not None:
        if not isinstance(amount, Decimal):
            amount = Decimal(amount)
        amount = amount.quantize(Decimal("1." + "0" * decimals))

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

