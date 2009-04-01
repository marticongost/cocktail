#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.html import Element
from cocktail.html.databoundcontrol import DataBoundControl

class CheckBox(Element, DataBoundControl):

    tag = "input"
    
    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        DataBoundControl.__init__(self)
        self["type"] = "checkbox"

    def _get_value(self):
        return self["checked"] or False
    
    def _set_value(self, value):
        self["checked"] = bool(value)

    value = property(_get_value, _set_value, doc = """
        Gets or sets the checkbox's value.
        @type: bool
        """)

    def insert_into_form(self, form, field_instance):
        field_instance.insert(0, self)

        # Disable the 'required' mark for this field, as it doesn't make sense
        # on a checkbox
        required_mark = getattr(field_instance.label, "required_mark", None)

        if required_mark:
            required_mark.visible = False

