#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.html import Element


class CheckBox(Element):

    tag = "input"
    is_form_control = True

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self["type"] = "checkbox"

    def _ready(self):
        self["checked"] = bool(self.value)

    def insert_into_form(self, form, field_instance):
        field_instance.insert(0, self)

        # Disable the 'required' mark for this field, as it doesn't make sense
        # on a checkbox
        required_mark = getattr(field_instance.label, "required_mark", None)

        if required_mark:
            required_mark.visible = False

