#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.schema import String
from cocktail.html import Element
from cocktail.controllers.parameters import serialize_parameter


class TextBox(Element):

    tag = "input"
    is_form_control = True
    spellcheck = None

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self["type"] = "text"

    def _ready(self):

        value = self.value
        spellcheck = self.spellcheck

        if self.member:
            try:
                value = serialize_parameter(self.member, value)
            except:
                pass

            # Limit the length of the control
            if isinstance(self.member, String) \
            and self.member.max is not None:
                self["maxlength"] = str(self.member.max)

            if spellcheck is None:
                spellcheck = self.member.spellcheck

        if spellcheck:
            self["spellcheck"] = True

        self["value"] = value
        Element._ready(self)

