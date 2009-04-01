#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from __future__ import with_statement
from decimal import Decimal
from unittest import TestCase
from cocktail.translations import translate, language_context


class DecimalTranslationTestCase(TestCase):

    def test_translate(self):

        ca_es_values = (
            (Decimal("0"), "0"),
            (Decimal("-0"), "-0"), # Heh...
            (Decimal("+0"), "0"), # Heh...
            (Decimal("1"), "1"),
            (Decimal("+1"), "1"),
            (Decimal("105"), "105"),
            (Decimal("50.0"), "50,0"),
            (Decimal("150.25"), "150,25"),
            (Decimal("0.3333"), "0,3333"),
            (Decimal("5000"), "5.000"),
            (Decimal("100000"), "100.000"),
            (Decimal("5.000"), "5,000"),
            (Decimal("100.000"), "100,000"),
            (Decimal("15000.03"), "15.000,03"),
            (Decimal("250000.3"), "250.000,3"),
            (Decimal("-1"), "-1"),
            (Decimal("-105"), "-105"),
            (Decimal("-50.0"), "-50,0"),
            (Decimal("-150.25"), "-150,25"),
            (Decimal("-0.3333"), "-0,3333"),
            (Decimal("-5000"), "-5.000"),
            (Decimal("-100000"), "-100.000"),
            (Decimal("-5.000"), "-5,000"),
            (Decimal("-100.000"), "-100,000"),
            (Decimal("-15000.03"), "-15.000,03"),
            (Decimal("-250000.3"), "-250.000,3")
        )

        values = (
            ("ca", ca_es_values),
            ("en", (
                (Decimal("0"), "0"),
                (Decimal("-0"), "-0"), # Again...
                (Decimal("+0"), "0"),
                (Decimal("1"), "1"),
                (Decimal("+1"), "1"),
                (Decimal("105"), "105"),
                (Decimal("50.0"), "50.0"),
                (Decimal("150.25"), "150.25"),
                (Decimal("0.3333"), "0.3333"),
                (Decimal("5000"), "5,000"),
                (Decimal("100000"), "100,000"),
                (Decimal("5.000"), "5.000"),
                (Decimal("100.000"), "100.000"),
                (Decimal("15000.03"), "15,000.03"),
                (Decimal("250000.3"), "250,000.3"),
                (Decimal("-1"), "-1"),
                (Decimal("-105"), "-105"),
                (Decimal("-50.0"), "-50.0"),
                (Decimal("-150.25"), "-150.25"),
                (Decimal("-0.3333"), "-0.3333"),
                (Decimal("-5000"), "-5,000"),
                (Decimal("-100000"), "-100,000"),
                (Decimal("-5.000"), "-5.000"),
                (Decimal("-100.000"), "-100.000"),
                (Decimal("-15000.03"), "-15,000.03"),
                (Decimal("-250000.3"), "-250,000.3")
            ))
        )

        for language, language_values in values:
            with language_context(language):
                for raw, expected in language_values:
                    self.assertEqual(translate(raw), expected)

