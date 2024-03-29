#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from cocktail.schema.schemastrings import String


class EmailAddress(String):

    _format = re.compile("^.*@.*$")
    display = "cocktail.html.MailToLink"

