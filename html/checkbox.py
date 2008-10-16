#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.html import Element

class CheckBox(Element):

    tag = "input"

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self["type"] = "checkbox"

    def _ready(self):
        self._bind_name(self.member, self.language)
        Element._ready(self)

    def _get_value(self):
        return self["checked"] or False
    
    def _set_value(self, value):
        self["checked"] = bool(value)

    value = property(_get_value, _set_value, doc = """
        Gets or sets the checkbox's value.
        @type: bool
        """)

