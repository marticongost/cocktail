#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html import Element


class HiddenInput(Element):

    tag = "input"

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self["type"] = "hidden"

    def _ready(self):

        if self.member:
            self._bind_name(self.member, self.language)
    
        Element._ready(self)

    def _get_value(self):
        return self["value"]
    
    def _set_value(self, value):
        self["value"] = value

    value = property(_get_value, _set_value, doc = """
        Gets or sets the value of the input.
        @type: str
        """)

