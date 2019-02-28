#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import dateutils
from cocktail.translations import translations
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

        kwargs.setdefault(
            "normalization",
            lambda value:
                dateutils.CalendarPage(*value)
                if isinstance(value, tuple)
                else value
        )

        Tuple.__init__(self, *args, **kwargs)

    def translate_value(self, value, language = None, **kwargs):
        if value:
            return translations(value, language, **kwargs)
        else:
            return Tuple.translate_value(self, value, language, **kwargs)

