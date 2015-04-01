#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html import Element
from cocktail.controllers.parameters import serialize_parameter


class HiddenInput(Element):

    tag = "input"
    styled_class = False
    is_form_control = True

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self["type"] = "hidden"

    def _ready(self):

        value = self.value

        if self.member:
            try:
                value = serialize_parameter(self.member, value)
            except:
                pass

        self["value"] = value
        Element._ready(self)

