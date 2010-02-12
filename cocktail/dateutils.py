#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
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

