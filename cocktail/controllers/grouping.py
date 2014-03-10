#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail.pkgutils import get_full_name
from cocktail.modeling import getter
from cocktail.translations import translations, get_language
from cocktail.schema import Member, Date, Time, DateTime
from cocktail.schema.expressions import (
    PositiveExpression,
    NegativeExpression
)
from datetime import date, datetime


class MemberGrouping(object):

    member = None
    language = None
    variants = ()
    variant = None
    sign = PositiveExpression

    def get_grouping_value(self, item):
        return item.get(self.member, self.language)

    @getter
    def order(self):
        expr = self.member
        if self.language:
            expr = expr.translated_into(self.language)
        return self.sign(expr)

    @getter
    def request_value(self):
        if self.member is None:
            return None
        else:
            value = self.member.name
            if self.sign is NegativeExpression:
                value = "-" + value
            if self.language:
                value += "." + self.language
            if self.variant:
                value += "!" + self.variant
            return value

    def translate_grouping_value(self, value, language = None, **kwargs):
        
        if value is not None:
            for cls in self.__class__.__mro__:
                translation = translations(
                    get_full_name(cls) + " value",
                    language,
                    grouping = self,
                    value = value,
                    **kwargs
                )                
                if translation:
                    return translation
                if cls is MemberGrouping:
                    break

        return translations(value, language, **kwargs)

    @classmethod
    def translate_grouping_variant(cls, variant, language = None):

        if not variant:
            variant = "default"

        for grouping_class in cls.__mro__:

            variant_translation = translations(
                get_full_name(grouping_class) + " %s variant" % variant,
                language
            )

            if variant_translation:
                return variant_translation

            if cls is MemberGrouping:
                break

        return u""


class DateGrouping(MemberGrouping):

    variants = "day", "month", "year"

    def get_grouping_value(self, item):
        
        value = item.get(self.member, self.language)
        
        if value is not None:
            if self.variant == "day":
                return date(value.year, value.month, value.day)

            elif self.variant == "month":
                return date(value.year, value.month, 1)

            elif self.variant == "year":
                return date(value.year, 1, 1)

        return value


class TimeGrouping(MemberGrouping):

    variants = "hour",

    def get_grouping_value(self, item):

        value = item.get(self.member, self.language)

        if value is not None and self.variant == "hour":
            return datetime(value.year, value.month, value.day, value.hour)
        else:
            return value


class DateTimeGrouping(DateGrouping, TimeGrouping):

    variants = TimeGrouping.variants + DateGrouping.variants

    def get_grouping_value(self, item):

        if self.variant == "hour":
            return TimeGrouping.get_grouping_value(self, item)
        else:
            return DateGrouping.get_grouping_value(self, item)


Member.grouping = MemberGrouping
Date.grouping = DateGrouping
Time.grouping = TimeGrouping
DateTime.grouping = DateTimeGrouping

