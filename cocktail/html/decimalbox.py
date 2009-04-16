#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from decimal import Decimal
from cocktail.html.textbox import TextBox
from cocktail.translations import translations


class DecimalBox(TextBox):

    def _get_value(self):
        return self["value"]
    
    def _set_value(self, value):

        if value is not None:

            if isinstance(value, Decimal):
                value = translations(value)

        self["value"] = value

    value = property(_get_value, _set_value, doc = """
        Gets or sets the textbox's value.
        @type: str
        """)

