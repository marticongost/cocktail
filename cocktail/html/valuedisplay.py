#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html.element import Element


class ValueDisplay(Element):

    tag = "span"
    translation_options = None

    def _ready(self):

        if self.member:
            value = self.translate_value(self.value)
        else:
            value = unicode(self.value)

        self.append(value)

    def translate_value(self, value):
        if self.translation_options is None:
            return self.member.translate_value(value)
        else:
            return self.member.translate_value(
                value,
                **self.translation_options
            )

