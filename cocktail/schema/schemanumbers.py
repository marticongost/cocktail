#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2008
"""
import decimal
import fractions
from cocktail.translations import translations
from cocktail.schema.member import Member
from cocktail.schema.validationcontext import ValidationContext
from cocktail.schema.rangedmember import RangedMember


class Number(Member, RangedMember):
    """Base class for all members that handle numeric values."""

    def __init__(self, *args, **kwargs):
        Member.__init__(self, *args, **kwargs)
        RangedMember.__init__(self)

    def _default_validation(self, context):

        for error in Member._default_validation(self, context):
            yield error

        for error in self._range_validation(context):
            yield error


class Integer(Number):
    """A numeric field limited integer values."""
    type = int

    def get_possible_values(self, context = None):
        values = Number.get_possible_values(self, context)

        if values is None and self.min is not None and self.max is not None:
            if context is None:
                context = ValidationContext(self, None)
            min_value = self.resolve_constraint(self.min, context)
            max_value = self.resolve_constraint(self.max, context)
            if min_value is not None and max_value is not None:
                values = list(range(min_value, max_value + 1))

        return values


class Float(Number):
    """A numeric field limited to float values."""
    type = float


class Decimal(Number):
    """A numeric field limited to decimal values."""
    type = decimal.Decimal

    def translate_value(self, value, language = None, **kwargs):
        if value is None:
            return ""
        else:
            return translations(value, language, **kwargs)

    def to_json_value(self, value, **options):

        if value is None:
            return None

        return str(value)

    def from_json_value(self, value, **options):

        if value is None:
            return None

        return self.type(value)


class Fraction(Number):
    """A numeric field limited to fractional values."""
    type = fractions.Fraction

    def to_json_value(self, value, **options):

        if value is None:
            return None

        return str(value)

    def from_json_value(self, value, **options):

        if value is None:
            return None

        return self.type(value)

