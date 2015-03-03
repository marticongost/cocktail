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

    def create_entry(self, item):

        entry = Element()
        entry.add_class("radio_entry")

        entry.input = Element("input")
        entry.input["type"] = "radio"
        entry.input["value"] = self.get_item_value(item)
        entry.input["checked"] = self.is_selected(item)
        entry.input["name"] = self.name
        entry.append(entry.input)

        entry.label = self.create_label(item)
        if entry.label.tag == "label":
            entry.label["for"] = entry.input.require_id()
        entry.append(entry.label)

        return entry

    def create_label(self, item):
        label = Element("label")
        label.append(self.get_item_label(item))
        return label

