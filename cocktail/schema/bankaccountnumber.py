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

    edit_control = "cocktail.html.MaskedInputBox"
    input_mask = "9999-9999-99-9999999999"
    min = 20
    max = 20

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("format", r"^\d{20}$")
        String.__init__(self, *args, **kwargs)
        self.add_validation(BankAccountNumber.bank_account_validation_rule)

    def normalization(self, value):
        if isinstance(value, basestring):
            value = divider_expr.sub("", value)
        return value

    def bank_account_validation_rule(self, value, context):
        """Validation rule for european bank account numbers."""

        if isinstance(value, basestring) and not self.checksum(value):
            yield BankAccountChecksumError(
                self, value, context
            )

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
