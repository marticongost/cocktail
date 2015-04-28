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
    is_form_control = True
    spellcheck = None

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("rows", 4)
        kwargs.setdefault("cols", 20)
        Element.__init__(self, *args, **kwargs)

    def _ready(self):

        value = self.value
        spellcheck = self.spellcheck

        if self.member:
            try:
                value = serialize_parameter(self.member, value)
            except:
                pass

            if spellcheck is None:
                spellcheck = self.member.spellcheck

        if spellcheck == False:
            self["spellcheck"] = False

        if value:
            self.append(value)

        Element._ready(self)

