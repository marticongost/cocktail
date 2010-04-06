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
from cocktail.translations import translations, language_context


class DecimalTranslationTestCase(TestCase):

    def test_translate(self):

        values = (
            (["ca", "es"],  (
                (Decimal("0"), "0"),
                (Decimal("-0"), "-0"), # Heh...
                (Decimal("+0"), "0"), # Heh...
                (Decimal("1"), "1"),
                (Decimal("+1"), "1"),
                (Decimal("105"), "105"),
                (Decimal("50.0"), "50,0"),
                (Decimal("50.00"), "50,00"),
                (Decimal("150.25"), "150,25"),
                (Decimal("150.2500"), "150,2500"),
                (Decimal("0.3333"), "0,3333"),
                (Decimal("0.04"), "0,04"),
                (Decimal("0.00007"), "0,00007"),
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
                (Decimal("-0.04"), "-0,04"),
                (Decimal("-0.00007"), "-0,00007"),
                (Decimal("-5000"), "-5.000"),
                (Decimal("-100000"), "-100.000"),
                (Decimal("-5.000"), "-5,000"),
                (Decimal("-100.000"), "-100,000"),
                (Decimal("-15000.03"), "-15.000,03"),
                (Decimal("-250000.3"), "-250.000,3")
            )),
            (["en"], (
                (Decimal("0"), "0"),
                (Decimal("-0"), "-0"), # Again...
                (Decimal("+0"), "0"),
                (Decimal("1"), "1"),
                (Decimal("+1"), "1"),
                (Decimal("105"), "105"),
                (Decimal("50.0"), "50.0"),
                (Decimal("50.00"), "50.00"),
                (Decimal("150.25"), "150.25"),
                (Decimal("150.2500"), "150.2500"),
                (Decimal("0.3333"), "0.3333"),
                (Decimal("0.04"), "0.04"),
                (Decimal("0.00007"), "0.00007"),
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
                (Decimal("-0.04"), "-0.04"),
                (Decimal("-0.00007"), "-0.00007"),
                (Decimal("-5000"), "-5,000"),
                (Decimal("-100000"), "-100,000"),
                (Decimal("-5.000"), "-5.000"),
                (Decimal("-100.000"), "-100.000"),
                (Decimal("-15000.03"), "-15,000.03"),
                (Decimal("-250000.3"), "-250,000.3")
            ))
        )

        for languages, tests in values:
            for language in languages:
                with language_context(language):
                    for raw, expected in tests:
                        assert translations(raw) == expected

