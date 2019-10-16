#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from unittest import TestCase
from nose.tools import assert_raises


class TranslationsTestCase(TestCase):

    def setUp(self):
        from cocktail.translations import set_language
        set_language(None)

    def tearDown(self):
        from cocktail.translations import set_language
        set_language(None)

    def test_returns_empty_string_for_undefined_key(self):
        from cocktail.translations.translation import Translations
        translations = Translations()
        translations.define("parrot", es = "Loro")
        assert translations("parrot", "en") == ""

    def test_translates_keys(self):

        from cocktail.translations import translations

        translations.define("parrot",
            ca = "Lloro",
            es = "Loro",
            en = "Parrot"
        )

        assert translations("parrot", "ca") == "Lloro"
        assert translations("parrot", "es") == "Loro"
        assert translations("parrot", "en") == "Parrot"

    def test_uses_implicit_language(self):

        from cocktail.translations import translations, set_language

        translations.define("parrot",
            ca = "Lloro",
            es = "Loro",
            en = "Parrot"
        )

        set_language("ca")
        assert translations("parrot") == "Lloro"

    def test_fails_with_undefined_implicit_language(self):

        from cocktail.translations import (
            translations,
            get_language,
            NoActiveLanguageError
        )

        translations.define("parrot",
            ca = "Lloro",
            es = "Loro",
            en = "Parrot"
        )

        assert_raises(NoActiveLanguageError, translations, "parrot")

