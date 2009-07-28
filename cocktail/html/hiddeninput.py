#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html import Element
from cocktail.html.databoundcontrol import DataBoundControl


class HiddenInput(Element, DataBoundControl):

    tag = "input"

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        DataBoundControl.__init__(self)
        self["type"] = "hidden"

    def _ready(self):

        if self.member:
            value = self["value"]
            if value is not None:
                try:
                    self["value"] = self.member.serialize_request_value(value)
                except:
                    pass
    
        Element._ready(self)

    def _get_value(self):
        return self["value"]
    
    def _set_value(self, value):
        self["value"] = value

    value = property(_get_value, _set_value, doc = """
        Gets or sets the value of the input.
        @type: str
        """)

