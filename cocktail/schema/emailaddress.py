#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from cocktail.schema.schemastrings import String


class EmailAddress(String):
    
    _format = re.compile("^.*@.*$")

