#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html import templates
from cocktail.html.utils import rendering_html5

TextBox = templates.get_class("cocktail.html.TextBox")


class PhoneNumberBox(TextBox):

    def _ready(self):
        TextBox._ready(self)
        if rendering_html5():
            self["type"] = "tel"

