#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from cocktail.schema.schemastrings import String
from cocktail.schema.exceptions import CreditCardChecksumError

whitespace_expr = re.compile(r"\s*")


class CreditCardNumber(String):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("format", r"^\d{8,19}$")
        String.__init__(self, *args, **kwargs)

    def normalization(self, value):
        if isinstance(value, basestring):
            value = whitespace_expr.sub("", value)
        return value

    def string_validation_rule(self, value, context):
        """Validation rule for credit card numbers. Checks the control
        digit.
        """
        if isinstance(value, basestring) and not self.checksum(value):
            if min is not None and len(value) < min:
                yield CreditCardChecksumError(
                    self, value, context, min
                )

    @classmethod
    def checksum(cls, number):
        checksum = 0
        digit = 0
        addend = 0
        even = False

        for c in number[::-1]:
            d = int(c)
            if even:
                addend = d * 2
                if addend > 9:
                    addend -= 9
            else:
                addend = d

            checksum += addend
            even = not even

        return checksum % 10 == 0

