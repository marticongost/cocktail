#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from cocktail.schema.schemastrings import String

_reg_expr = re.compile(r"^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$")


class SWIFTBIC(String):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("format", _reg_expr)
        String.__init__(self, *args, **kwargs)

