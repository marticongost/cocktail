#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from cocktail.schema.member import Member


class RegularExpression(Member):

    regular_expression_flags = 0

    def normalization(self, value):
        if isinstance(value, basestring):
            return re.compile(value, self.regular_expression_flags)
        else:
            return value

