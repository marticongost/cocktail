#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html.element import Element


class MailToLink(Element):

    tag = "a"

    def _ready(self):

        if self.value:
            self["href"] = "mailto:" + self.value
            self.append(self.value)

        Element._ready(self)

