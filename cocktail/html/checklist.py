#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html import Element, templates
from cocktail.html.selector import Selector

CheckBox = templates.get_class("cocktail.html.CheckBox")


class CheckList(Selector):

    empty_option_displayed = False

    def _ready(self):

        if not self.name and self.data_display:
            self.name = self.data_display.get_member_name(
                self.member,
                self.language
            )

        Selector._ready(self)
    
    def create_entry(self, value, label, selected):

        entry = Element()

        entry.check = CheckBox()
        entry.check["name"] = self.name
        entry.check.value = selected
        entry.check["value"] = value
        entry.append(entry.check)

        entry.label = Element("label")
        entry.label["for"] = entry.check.require_id()
        entry.label.append(label)
        entry.append(entry.label)

        return entry

    def insert_into_form(self, form, field_instance):
        
        field_instance.append(self)

        # Disable the 'required' mark for this field, as it doesn't make sense
        # on a checklist
        required_mark = getattr(field_instance.label, "required_mark", None)

        if required_mark and \
        not (self.member and \
        self.member.min and \
        isinstance(self.member.min, int) and \
        self.member.min > 0):
            required_mark.visible = False

