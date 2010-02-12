#-*- coding: utf-8 -*-
u"""
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
from cocktail.translations import translations

def get_max_day(context):

    date = context.validable

    if date.year is not None and (0 < date.month <= 12):
        return monthrange(date.year, date.month)[1]

    return None

class BaseDateTime(Schema, RangedMember):
    """Base class for all members that handle date and/or time values."""
    _is_date = False
    _is_time = False
   
    def __init__(self, *args, **kwargs):
        
        Schema.__init__(self, *args, **kwargs)
        RangedMember.__init__(self)

        day_kw = {"name": "day", "min": 1, "max": get_max_day}
        month_kw = {"name": "month", "min": 1, "max": 12}
        year_kw = {"name": "year"}
        hour_kw = {"name": "hour", "min": 0, "max": 23}
        minute_kw = {"name": "minute", "min": 0, "max": 59}
        second_kw = {"name": "second", "min": 0, "max": 59}

        day_properties = kwargs.pop("day_properties", None)
        month_properties = kwargs.pop("month_properties", None)
        year_properties = kwargs.pop("year_properties", None)
        hour_properties = kwargs.pop("hour_properties", None)
        minute_properties = kwargs.pop("minute_properties", None)
        second_properties = kwargs.pop("second_properties", None)

        if day_properties:
            day_kw.update(day_properties)

        if month_properties:
            month_kw.update(month_properties)

        if year_properties:
            year_kw.update(year_properties)

        if hour_properties:
            hour_kw.update(hour_properties)

        if minute_properties:
            minute_kw.update(minute_properties)

        if second_properties:
            second_kw.update(second_properties)

        if self._is_date:
            self.add_member(Integer(**day_kw))
            self.add_member(Integer(**month_kw))
            self.add_member(Integer(**year_kw))
        
        if self._is_time:
            self.add_member(Integer(**hour_kw))
            self.add_member(Integer(**minute_kw))
            self.add_member(Integer(**second_kw))


class DateTime(BaseDateTime):
    type = datetime.datetime
    _is_date = True
    _is_time = True
    translate_value = translations


class Date(BaseDateTime):
    type = datetime.date
    _is_date = True
    translate_value = translations


class Time(BaseDateTime):
    type = datetime.time
    _is_time = True

