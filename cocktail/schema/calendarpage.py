#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import dateutils
from cocktail.schema.schemanumbers import Integer
from cocktail.schema.schematuples import Tuple
from cocktail.schema.month import Month


class CalendarPage(Tuple):

    type = dateutils.CalendarPage
    request_value_separator = "-"

    def __init__(self, *args, **kwargs):

        year_params = kwargs.pop("year_params", None) or {}
        year_params.setdefault("required", True)

        month_params = kwargs.pop("month_params", None) or {}
        month_params.setdefault("required", True)

        kwargs["items"] = (
            Integer("year", **year_params),
            Month("month", **month_params)
        )

        Tuple.__init__(self, *args, **kwargs)

