#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
import datetime

HOUR_SECONDS = 60 * 60
DAY_SECONDS = HOUR_SECONDS * 24

def split_seconds(seconds, include_days = True):

    ms = int((seconds - int(seconds)) * 1000)

    if include_days:
        days, seconds = divmod(seconds, DAY_SECONDS)

    hours, seconds = divmod(seconds, HOUR_SECONDS)
    minutes, seconds = divmod(seconds, 60)

    if include_days:
        return (days, hours, minutes, seconds, ms)
    else:
        return (hours, minutes, seconds, ms)

def get_next_month(month_tuple):
    year, month = month_tuple
    month += 1
    if month > 12:
        month = 1
        year += 1
    return year, month

def get_previous_month(month_tuple):
    year, month = month_tuple
    month -= 1
    if month < 1:
        month = 12
        year -= 1
    return year, month

def add_time(value, time_fragment = None):
    if not isinstance(value, datetime.datetime):
        if time_fragment is None:
            time_fragment = datetime.time()
        value = datetime.datetime.combine(value, time_fragment)
    return value


class CalendarPage(tuple):

    def __new__(type, year, month):
        return tuple.__new__(type, (year, month))

    def __repr__(self):
        return self.__class__.__name__ + tuple.__repr__(self)

    @classmethod
    def current(cls):
        today = datetime.date.today()
        return cls(today.year, today.month)

    @property
    def year(self):
        return self[0]

    @property
    def month(self):
        return self[1]

    def __add__(self, n):
        year, month = self
        q, r = divmod(month + n, 12)
        if not r:
            r = 12
            if q < 0:
                q += 1
            else:
                q -= 1
        return self.__class__(year + q, r)

    def __sub__(self, n):
        return self + (-n)

    def start(self):
        return datetime.date(self[0], self[1], 1)

    def start_time(self):
        return datetime.datetime(self[0], self[1], 1)

    def date_range(self):
        return (self.start(), (self + 1).start())

    def time_range(self):
        return (self.start_time(), (self + 1).start_time())

