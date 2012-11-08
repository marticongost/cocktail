#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations
from cocktail.schema.schemanumbers import Integer


class Month(Integer):

    edit_control = "cocktail.html.DropdownSelector"
    min = 1
    max = 12

    def translate_value(self, value, language = None, **kwargs):
        return translations("month %d" % (value,))


