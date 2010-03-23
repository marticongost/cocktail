#-*- coding: utf-8 -*-
u"""

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
        from cocktail.translations import TranslationsRepository
        translations = TranslationsRepository()
        translations.define("parrot", es = u"Loro")
        assert translations("parrot", "en") == ""

    def test_translates_keys(self):

        from cocktail.translations import translations
        
        translations.define("parrot",
            ca = u"Lloro",
            es = u"Loro",
            en = u"Parrot"
        )

        assert translations("parrot", "ca") == u"Lloro"
        assert translations("parrot", "es") == u"Loro"
        assert translations("parrot", "en") == u"Parrot"

    def test_uses_implicit_language(self):

        from cocktail.translations import translations, set_language
        
        translations.define("parrot",
            ca = u"Lloro",
            es = u"Loro",
            en = u"Parrot"
        )

        set_language("ca")
        assert translations("parrot") == u"Lloro"

    def test_fails_with_undefined_implicit_language(self):

        from cocktail.translations import (
            translations,
            get_language,
            NoActiveLanguageError
        )

        translations.define("parrot",
            ca = u"Lloro",
            es = u"Loro",
            en = u"Parrot"
        )

        assert_raises(NoActiveLanguageError, translations, "parrot")

