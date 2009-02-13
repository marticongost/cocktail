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
        entry = Element()
        
        input = Element("input")        
        input["type"] = "radio"
        input["value"] = value
        input["checked"] = selected        
        input["name"] = self.name
        entry.append(input)
        
        entry.append(label)

        return entry

