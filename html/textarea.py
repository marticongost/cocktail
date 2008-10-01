#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.html import Element

class TextArea(Element):

    tag = "textarea"

    def _ready(self):

        if self.member:
            
            # Name binding
            self["name"] = self.member.name

        Element._ready(self)

