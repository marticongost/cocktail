#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html.element import Element


class ValueDisplay(Element):

    tag = "span"

    def _ready(self):

        if self.member:
            value = self.member.translate_value(self.value)
        else:
            value = unicode(self.value)

        self.append(value)

