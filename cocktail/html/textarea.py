#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.controllers.parameters import serialize_parameter
from cocktail.html import Element, Content


class TextArea(Element):

    tag = "textarea"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("rows", 4)
        kwargs.setdefault("cols", 20)
        Element.__init__(self, *args, **kwargs)

    def _ready(self):

        value = self.value

        if self.member:
            try:
                value = serialize_parameter(self.member, value)
            except:
                pass

        if value:
            self.append(value)

        Element._ready(self)

