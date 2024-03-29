#-*- coding: utf-8 -*-
"""
Provides classes to describe members that take dates and times as values.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2008
"""
from typing import Optional
from datetime import datetime, date, time, timedelta
from calendar import monthrange
from cocktail.translations import translations
from cocktail.schema.member import Member, translate_member
from cocktail.schema.schema import Schema
from cocktail.schema.rangedmember import RangedMember
from cocktail.schema.schemanumbers import Integer
from cocktail.schema.validationcontext import ValidationContext
from cocktail.translations import translations

def get_max_day(context):

    date = context.parent_context and context.parent_context.value

    if date and date.year is not None and (0 < date.month <= 12):
        return monthrange(date.year, date.month)[1]

    return None


class BaseDateTime(Schema, RangedMember):
    """Base class for all members that handle date and/or time values."""
    _is_date = False
    _is_time = False
    text_search = False

    def __init__(self, *args, **kwargs):

        kwargs.setdefault("default", None)
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

    def _default_validation(self, context):

        for error in Schema._default_validation(self, context):
            yield error

        for error in self._range_validation(context):
            yield error

    def _create_default_instance(self):
        return None

    def extract_searchable_text(self, extractor):
        Member.extract_searchable_text(self, extractor)

    def _infer_is_language_dependant(self):
        return True


class DateTime(BaseDateTime):
    type = datetime
    _is_date = True
    _is_time = True
    translate_value = translations

    def to_json_value(self, value, **options):

        if value is None:
            return value

        return value.isoformat()

    def from_json_value(self, value, **options):
        return self.parse(value, **options) if value else None

    def serialize(self, value: datetime, **options) -> str:
        if not value:
            return ""
        else:
            return value.isoformat()

    def parse(self, value: str, **options) -> Optional[datetime]:

        if not value.strip():
            return None

        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")


class Date(BaseDateTime):
    type = date
    _is_date = True
    translate_value = translations

    def get_possible_values(self, context = None):
        values = BaseDateTime.get_possible_values(self, context)

        if values is None and self.min is not None and self.max is not None:
            if context is None:
                context = ValidationContext(self, None)
            min_value = context.resolve_constraint(self.min)
            max_value = context.resolve_constraint(self.max)
            if min_value is not None and max_value is not None:
                one_day = timedelta(days = 1)
                values = []
                d = min_value
                while d < max_value:
                    values.append(d)
                    d += one_day

        return values

    def to_json_value(self, value, **options):

        if value is None:
            return value

        return value.isoformat()

    def from_json_value(self, value, **options):
        return self.parse(value, **options) if value else None

    def serialize(self, value: date, **options) -> str:
        return value.isoformat()

    def parse(self, value: str, **options) -> Optional[date]:
        if not value.strip():
            return None
        return datetime.strptime(value, "%Y-%m-%d").date()


class Time(BaseDateTime):
    type = time
    _is_time = True

    def to_json_value(self, value, **options):

        if value is None:
            return value

        return value.isoformat()

    def from_json_value(self, value, **options):
        return self.parse(value, **options) if value else None

    def serialize(self, value: time, **options) -> str:
        return value.isoformat()

    def parse(self, value: str, **options) -> Optional[time]:
        if not value.strip():
            return None
        return datetime.strptime(value, "%H:%M:%S.%f").time()


translations.instances_of(BaseDateTime)(translate_member)

