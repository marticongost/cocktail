#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html.element import Element
from cocktail.html.selector import Selector


class RadioSelector(Selector):

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
        
        entry.input = Element("input")
        entry_id = entry.input.require_id()
        entry.input["type"] = "radio"
        entry.input["value"] = value
        entry.input["checked"] = selected
        entry.input["name"] = self.name
        entry.append(entry.input)
        
        entry.label = Element("label")
        entry.label["for"] = entry_id
        entry.label.append(label)
        entry.append(entry.label)

        return entry

