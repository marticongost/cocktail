#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html.element import Element
from cocktail.html.selector import Selector


class RadioSelector(Selector):

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
        
        entry.input = Element("input")
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

