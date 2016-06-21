#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .translation import translations

translations.load_bundle("cocktail.translations.localetranslations")

def translate_locale(locale, language = None):

    if not locale:
        return ""

    trans = translations(
        "cocktail.locales." + locale.replace("-", "."),
        language
    )
    if trans:
        return trans

    return u"".join(
        translations(
            "cocktail.locale_component." + component,
            language,
            locale = locale,
            index = index
        )
        or translations(
            "cocktail.locale_component",
            language,
            locale = locale,
            component = component,
            index = index
        )
        or (u" - " if index else u"") + component
        for index, component in enumerate(locale.split("-"))
    )

def translate_locale_component(locale, component, index, language = None):
    if index == 0:
        return translations("cocktail.locales." + component, language)

translations.definitions["cocktail.locale_component"] = translate_locale

