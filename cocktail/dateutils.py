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
    if isinstance(value, datetime.date):
        if time_fragment is None:
            time_fragment = datetime.time()
        value = datetime.datetime.combine(value, time_fragment)
    return value

