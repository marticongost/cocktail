#-*- coding: utf-8 -*-
"""

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
        entry_id = entry.require_id()

        entry.check = CheckBox()
        entry.check["name"] = self.name
        entry.check["id"] = entry_id
        entry.check.value = selected
        entry.check["value"] = value
        entry.append(entry.check)

        entry.label = Element("label")
        entry.label["for"] = entry_id
        entry.label.append(label)
        entry.append(entry.label)

        return entry

