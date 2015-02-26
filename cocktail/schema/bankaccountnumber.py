#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
import re
from math import floor
from cocktail.schema.schemastrings import String
from cocktail.schema.exceptions import BankAccountChecksumError

divider_expr = re.compile(r"\-*")


class BankAccountNumber(String):

    input_mask = "9999-9999-99-9999999999"
    min = 20
    max = 20

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("format", r"^\d{20}$")
        String.__init__(self, *args, **kwargs)

    def normalization(self, value):
        if isinstance(value, basestring):
            value = divider_expr.sub("", value)
        return value

    def _default_validation(self, context):
        """Validation rule for european bank account numbers."""

        for error in String._default_validation(self, context):
            yield error

        if (
            isinstance(context.value, basestring)
            and not self.checksum(context.value)
        ):
            yield BankAccountChecksumError(context)

    @classmethod
    def checksum(cls, value):
        def proc(digits):
            result = 11 - sum(int(d)*2**i for i,d in enumerate(digits)) % 11
            return result if result < 10 else 11 - result
        return value[8:10] == '%d%d' % (proc('00'+value[0:8]), proc(value[10:20]))

    def translate_value(self, value, language = None, **kwargs):
        if value:
            return value[0:4] + u"-" + value[4:8] + u"-" + value[8:]
        else:
            return ""
