#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from time import time
from datetime import date, datetime, timedelta

def nearest_expiration(*args):
    """Obtains the nearest of any number of dates.

    See `normalize_expiration` for details on all the different ways of
    describing the dates.

    :return: Return the lowest of the provided dates, discarding `None`
        and expired values. If no suitable expiration date is found, return
        `None` instead.
    """
    now = time()
    expiration = None

    for value in args:
        if value is not None:
            value = normalize_expiration(value)
            if value > now and (expiration is None or value < expiration):
                expiration = value

    return expiration

def normalize_expiration(expiration):
    """Obtains a normalized representation of an expiration date.

    This method takes an expiration date expressed in any of several
    possible forms, and normalizes it to an integer timestamp.

    :param expiration: The value to normalize. Can take any of the
        following forms:

            - An integer will be interpreted as a timestamp.
            - A floating point number will be floored to an integer and
              treated as a timestamp.
            - A ``timedelta`` object will be added to the current time
              to obtain the timestamp.
            - A ``datetime`` object will be transformed into a timestamp.
            - A ``date`` object will be be transformed into a timestamp,
              assuming a time of 00:00:00.

    :raises TypeError: Raised if the given value doesn't match any of the
        acceptable types.
    """
    if isinstance(expiration, int):
        return expiration
    elif isinstance(expiration, float):
        return int(expiration)
    elif isinstance(expiration, timedelta):
        return int(time() + expiration.total_seconds())
    elif isinstance(expiration, (datetime, date)):
        return int(expiration.strftime("%s"))
    else:
        raise TypeError(
            "Invalid expiration: %r. Expected a value of type int, float, "
            "timedelta, datetime or datetime."
            % expiration
        )

