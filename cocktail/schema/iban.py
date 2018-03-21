#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from string import digits
from cocktail.schema.schemastrings import String
from cocktail.schema.exceptions import FormatError


class IBAN(String):

    reg_expr = re.compile(r"^[A-Za-z]{2}\d{2}[A-Za-z0-9]{1,30}$")

    length_by_country = {
        "AL": 28,
        "AD": 24,
        "AT": 20,
        "AZ": 28,
        "BH": 22,
        "BE": 16,
        "BA": 20,
        "BR": 29,
        "BG": 22,
        "CR": 21,
        "HR": 21,
        "CY": 28,
        "CZ": 24,
        "DK": 18,
        "FO": 18,
        "GL": 18,
        "DO": 28,
        "EE": 20,
        "FI": 18,
        "FR": 27,
        "GE": 22,
        "DE": 22,
        "GI": 23,
        "GR": 27,
        "GT": 28,
        "HU": 28,
        "IS": 26,
        "IE": 22,
        "IL": 23,
        "IT": 27,
        "JO": 30,
        "KZ": 20,
        "KW": 30,
        "LV": 21,
        "LB": 28,
        "LI": 21,
        "LT": 20,
        "LU": 20,
        "MK": 19,
        "MT": 31,
        "MR": 27,
        "MU": 30,
        "MD": 24,
        "MC": 27,
        "ME": 22,
        "NL": 18,
        "NO": 15,
        "PK": 24,
        "PS": 29,
        "PL": 28,
        "PT": 25,
        "RO": 24,
        "QA": 29,
        "SM": 27,
        "SA": 24,
        "RS": 22,
        "SK": 24,
        "SI": 19,
        "ES": 24,
        "SE": 24,
        "CH": 21,
        "TN": 24,
        "TR": 26,
        "AE": 23,
        "GB": 22,
        "VG": 24
    }

    # Special treatment for the 'reg_expr' attribute (regular expressions don't
    # support deep copying)
    _special_copy_keys = String._special_copy_keys | set(["reg_expr"])

    def _default_validation(self, context):

        for error in String._default_validation(self, context):
            yield error

        if context.value and not self.validate_iban_format(context.value):
            yield FormatError(context, "IBAN")

    @classmethod
    def validate_iban_format(cls, value):
        value = cls.normalization(value)

        # Validate the overall format
        if not cls.reg_expr.match(value):
            return False

        # Validate the value's length
        country = value[:2]
        expected_length = cls.length_by_country.get(country)
        if expected_length and len(value) != expected_length:
            return False

        # Validate control digits
        control = value[2:4]
        char_mod = 10 - ord("A")
        number = "".join(
            str(c if c in digits else ord(c) + char_mod)
            for c in value[4:] + value[:4]
        )
        if int(number) % 97 != 1:
            return False

        return True

    @classmethod
    def normalization(cls, value):
        return value and (
            value
                .strip()
                .upper()
                .replace(" ", "")
                .replace("-", "")
        )

    def translate_value(self, value, language = None, **kwargs):

        if value:
            value = value.upper()
            chunks = []

            while value:
                chunks.append(value[:4])
                value = value[4:]

            return "-".join(chunks)

        return ""

