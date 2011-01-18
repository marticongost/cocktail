#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html.textbox import TextBox


class ColorPicker(TextBox):

    def _build(self):
        self.add_resource("/cocktail/styles/colorpicker.css")
        self.add_resource("/cocktail/scripts/colorpicker.js")

