#-*- coding: utf-8 -*-
"""
Provides classes to describe members that take dates and times as values.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2008
"""
import datetime
from calendar import monthrange
from cocktail.schema.schema import Schema
from cocktail.schema.rangedmember import RangedMember
from cocktail.schema.schemanumbers import Integer

def get_max_day(value, context):

    date = context["validable"]

    if date.year is not None and 0 < date.month <= 12:
        return monthrange(date.year, date.month)[1]

    return None

class BaseDateTime(Schema, RangedMember):
    """Base class for all members that handle date and/or time values."""
    _is_date = False
    _is_time = False
   
    def __init__(self, **kwargs):
        
        Schema.__init__(self, **kwargs)
        RangedMember.__init__(self)

        if self._is_date:
            self.add_member(Integer(name = "day", min = 1, max = get_max_day))
            self.add_member(Integer(name = "month", min = 1, max = 12))
            self.add_member(Integer(name = "year"))
        
        if self._is_time:
            self.add_member(Integer(name = "hour", min = 0, max = 23))
            self.add_member(Integer(name = "minute", min = 0, max = 59))
            self.add_member(Integer(name = "second", min = 0, max = 59))


class DateTime(BaseDateTime):
    type = datetime.datetime
    _is_date = True
    _is_time = True


class Date(BaseDateTime):
    type = datetime.date
    _is_date = True


class Time(BaseDateTime):
    type = datetime.time
    _is_time = True

