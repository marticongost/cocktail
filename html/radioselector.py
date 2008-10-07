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

    def create_entry(self, value, label, selected):
        entry = Element("input")
        entry["type"] = "radio"
        entry["value"] = value
        entry["selected"] = selected        
        entry["name"] = self.name
        entry.append(label)
        return entry

