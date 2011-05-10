#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from cocktail.schema.schemastrings import String

color_regexp = re.compile("^#[0-9a-f]{6}$")


class Color(String):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("format", color_regexp)
        String.__init__(self, *args, **kwargs)

    def normalization(self, value):
        if value:
            value = value.lower()
            if not value.startswith("#"):
                value = "#" + value
            if len(value) == 4:
                value = "#" + "".join(c * 2 for c in value[1:])
        return value

