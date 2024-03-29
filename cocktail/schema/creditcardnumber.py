#-*- coding: utf-8 -*-
"""

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
        if isinstance(value, str):
            value = whitespace_expr.sub("", value)
        return value

    def _default_validation(self, context):
        """Validation rule for credit card numbers. Checks the control
        digit.
        """
        for error in String._default_validation(self, context):
            yield error

        if (
            isinstance(context.value, str)
            and not self.checksum(context.value)
        ):
            if min is not None and len(context.value) < min:
                yield CreditCardChecksumError(context)

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

