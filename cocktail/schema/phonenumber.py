#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.schema.schemastrings import String

PHONE_FORMAT = r"^(00)?\+?\d{1,15}$"


class PhoneNumber(String):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("format", PHONE_FORMAT)
        String.__init__(self, *args, **kwargs)

    def normalization(self, value):
        return value and value.replace(" ", "")

