"""Utilities for dealing with date and time values.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Iterator, Tuple, Union
import datetime
from cocktail.translations import translations, month_name, month_abbr

HOUR_SECONDS = 60 * 60
DAY_SECONDS = HOUR_SECONDS * 24


def split_seconds(
        seconds: int,
        include_days: bool = True) -> Union[
            Tuple[int, int, int, int],
            Tuple[int, int, int, int, int],
        ]:
    """Divides a number of seconds into a tuple of hours, minutes, seconds and
    milliseconds.

    :param seconds: The number of seconds to split.
    :param include_days: Whether to prepend an additional number in the tuple
        including the number of days.

    :return: A tuple indicating the value for each unit.
    """
    ms = int((seconds - int(seconds)) * 1000)

    if include_days:
        days, seconds = divmod(seconds, DAY_SECONDS)

    hours, seconds = divmod(seconds, HOUR_SECONDS)
    minutes, seconds = divmod(seconds, 60)

    if include_days:
        return (days, hours, minutes, seconds, ms)
    else:
        return (hours, minutes, seconds, ms)


def get_next_month(month_tuple: Tuple[int, int]) -> Tuple[int, int]:
    """Obtains the month following the given month.

    @param month_tuple: A year, month tuple indicating the source month.

    @return A year, month tuple specifying the month that follows the given
        month.
    """
    year, month = month_tuple
    month += 1
    if month > 12:
        month = 1
        year += 1
    return year, month


def get_previous_month(month_tuple: Tuple[int, int]) -> Tuple[int, int]:
    """Obtains the month preceding the given month.

    @param month_tuple: A year, month tuple indicating the source month.

    @return A year, month tuple specifying the month that precedes the given
        month.
    """
    year, month = month_tuple
    month -= 1
    if month < 1:
        month = 12
        year -= 1
    return year, month


def add_time(
        value: Union[datetime.date, datetime.datetime],
        time_fragment: datetime.time = None) -> datetime.datetime:
    """Normalizes date and datetime values to datetime.

    If the given value is already a datetime, it is returned as is. If it is a
    date, it is converted into a datetime object.

    @param value: The date or datetime to normalize.
    @param time_fragment: The time to append if the given value is a date. If
        not given the current time will be added instead.

    @return: The normalized datetime.
    """
    if not isinstance(value, datetime.datetime):
        if time_fragment is None:
            time_fragment = datetime.time()
        value = datetime.datetime.combine(value, time_fragment)
    return value


class CalendarPage(tuple):
    """A class representing a year, month tuple."""

    def __new__(type, *args):
        if len(args) == 1:
            year = args[0].year
            month = args[0].month
        else:
            year, month = args
        return tuple.__new__(type, (year, month))

    def __repr__(self):
        return self.__class__.__name__ + tuple.__repr__(self)

    @classmethod
    def current(cls) -> "CalendarPage":
        """Obtains a `CalendarPage` representing the current month."""
        today = datetime.date.today()
        return cls(today.year, today.month)

    @property
    def year(self) -> int:
        """Returns the year component."""
        return self[0]

    @property
    def month(self) -> int:
        """Returns the month component."""
        return self[1]

    def __add__(self, n: int) -> "CalendarPage":
        year, month = self
        q, r = divmod(month + n, 12)
        if not r:
            r = 12
            if q < 0:
                q += 1
            else:
                q -= 1
        return self.__class__(year + q, r)

    def __sub__(self, n: int) -> "CalendarPage":
        return self + (-n)

    def start(self) -> datetime.date:
        """Obtains the date object for the first day of the designated
        month.
        """
        return datetime.date(self[0], self[1], 1)

    def start_time(self) -> datetime.datetime:
        """Obtains the datetime object for the first day of the designated
        month.
        """
        return datetime.datetime(self[0], self[1], 1)

    def date_range(self) -> Tuple[datetime.date, datetime.date]:
        """Obtains a tuple with the first and last days of the designated
        month, as date objects.
        """
        return (self.start(), (self + 1).start())

    def time_range(self) -> Tuple[datetime.datetime, datetime.datetime]:
        """Obtains a tuple with the first and last days of the designated
        month, as datetime objects.
        """
        return (self.start_time(), (self + 1).start_time())

    def iter_towards(
            self,
            target_page: "CalendarPage") -> Iterator["CalendarPage"]:
        """Produces an iterable sequence of `CalendarPage` objects, from the
        starting point (the object itself) towards the target page (included).

        Note that the target page should be greater or equal than the source
        page.

        :param target_page: The page after which the iterator will stop.
        """
        page = self
        while True:
            yield page
            if page == target_page:
                break
            page += 1


@translations.instances_of(CalendarPage)
def _translate_calendar_page(page, abbreviated = False):
    return "%s %d" % (
        (month_abbr if abbreviated else month_name)(page[1]),
        page[0]
    )

