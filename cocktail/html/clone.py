#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html.element import Element


class Clone(Element):

    source = None

    def _render(self, rendering):
        if self.source is not None:
            self.source._render(rendering)

