#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html import templates
from cocktail.html.utils import rendering_html5

TextBox = templates.get_class("cocktail.html.TextBox")


class ColorPicker(TextBox):

    def _ready(self):
        TextBox._ready(self)
        if rendering_html5():
            self["type"] = "color"

