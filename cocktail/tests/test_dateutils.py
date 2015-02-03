#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from unittest import TestCase


class CalendarPageTestCase(TestCase):

    def test_supports_month_arithmetic(self):
        from cocktail.dateutils import CalendarPage

        p = CalendarPage(2012, 1)
        assert p + 0 == p
        assert p - 0 == p

        assert CalendarPage(2012, 6) + 1 == (2012, 7)
        assert CalendarPage(2012, 6) + 2 == (2012, 8)
        assert CalendarPage(2012, 6) + 6 == (2012, 12)
        assert CalendarPage(2012, 6) + 7 == (2013, 1)
        assert CalendarPage(2012, 6) + 10 == (2013, 4)
        assert CalendarPage(2012, 6) + 25 == (2014, 7)

        assert CalendarPage(2012, 6) - 1 == (2012, 5)
        assert CalendarPage(2012, 6) - 2 == (2012, 4)
        assert CalendarPage(2012, 6) - 5 == (2012, 1)
        assert CalendarPage(2012, 6) - 6 == (2011, 12)
        assert CalendarPage(2012, 6) - 10 == (2011, 8)
        assert CalendarPage(2012, 6) - 25 == (2010, 5)

