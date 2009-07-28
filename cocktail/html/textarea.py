#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.html import Element, Content
from cocktail.html.databoundcontrol import DataBoundControl


class TextArea(Element, DataBoundControl):
    tag = "textarea"

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        DataBoundControl.__init__(self)
        self.__content = Content()
        self.append(self.__content)

    def _ready(self):        
        if self.member:
            value = self.__content.value
            if value is not None:
                try:
                    self.__content.value = \
                        self.member.serialize_request_value(value)
                except:
                    pass

        Element._ready(self)

    def _get_value(self):
        return self.__content.value
    
    def _set_value(self, value):
        self.__content.value = value

    value = property(_get_value, _set_value, doc = """
        Gets or sets the text area's value.
        @type: str
        """)

