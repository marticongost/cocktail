#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.html import Element
from cocktail.html.databoundcontrol import DataBoundControl
from cocktail.schema import String

class TextBox(Element, DataBoundControl):

    tag = "input"

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        DataBoundControl.__init__(self)
        self["type"] = "text"

    def _ready(self):

        if self.member:

            value = self["value"]
            if value is not None:
                try:
                    self["value"] = self.member.serialize_request_value(value)
                except:
                    pass

            # Limit the length of the control
            if isinstance(self.member, String) \
            and self.member.max is not None:
                self["maxlength"] = str(self.member.max)
    
        Element._ready(self)

    def _get_value(self):
        return self["value"]
    
    def _set_value(self, value):
        self["value"] = value

    value = property(_get_value, _set_value, doc = """
        Gets or sets the textbox's value.
        @type: str
        """)

