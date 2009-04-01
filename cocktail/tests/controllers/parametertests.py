#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from __future__ import with_statement
from unittest import TestCase


class ParseTestCase(TestCase):
    
    def test_decimal(self):
        from decimal import Decimal
        from cocktail.schema import Decimal as DecimalMember
        from cocktail.controllers.parameters import FormSchemaReader
        from cocktail.translations import language_context
        reader = FormSchemaReader()
        member = DecimalMember()
        
        ca_es_values = (
            ("foo", "foo"),
            ("0", Decimal("0")),
            ("-0", Decimal("-0")),
            ("+0", Decimal("0")),
            ("1", Decimal("1")),
            ("+1", Decimal("1")),
            ("105", Decimal("105")),
            ("50,0", Decimal("50.0")),
            ("150,25", Decimal("150.25")),
            ("0,3333", Decimal("0.3333")),
            ("5000", Decimal("5000")),
            ("5.000", Decimal("5000")),
            ("100.000", Decimal("100000")),
            ("5,000", Decimal("5.000")),
            ("100,000", Decimal("100.000")),
            ("15.000,03", Decimal("15000.03")),
            ("250.000,3", Decimal("250000.3")),
            ("250,000.3", "250,000.3"),
            ("10.00.000", "10.00.000")
        )

        values = (
            ("ca", ca_es_values),
            ("en", (
                ("foo", "foo"),
                ("0", Decimal("0")),
                ("-0", Decimal("-0")),
                ("+0", Decimal("0")),
                ("1", Decimal("1")),
                ("+1", Decimal("1")),
                ("105", Decimal("105")),
                ("50.0", Decimal("50.0")),
                ("150.25", Decimal("150.25")),
                ("0.3333", Decimal("0.3333")),
                ("5,000", Decimal("5000")),
                ("100,000", Decimal("100000")),
                ("5000", Decimal("5000")),
                ("5.000", Decimal("5.000")),
                ("100.000", Decimal("100.000")),
                ("15,000.03", Decimal("15000.03")),
                ("250,000.3", Decimal("250000.3")),
                ("250.000,3", "250.000,3"),
                ("10,00,000", "10,00,000")
            ))
        )

        for language, language_values in values:
            with language_context(language):
                for raw, expected in language_values:
                    self.assertEqual(
                        member.parse_request_value(reader, raw),
                        expected
                    )        

