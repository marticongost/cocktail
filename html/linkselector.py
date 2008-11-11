#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html.element import Element
from cocktail.html.selector import Selector
from cocktail.controllers.viewstate import view_state


class LinkSelector(Selector):

    def create_entry(self, value, label, selected):
        
        entry = Element()

        if selected:
            entry.add_class("selected")

        link = self.create_entry_link(value, label)                
        entry.append(link)
        return entry

    def create_entry_link(self, value, label):

        link = Element("a")
        
        if self.name:
            name = self.name
            if isinstance(name, unicode):
                name = str(name)
            link["href"] = "?" + view_state(**{name: value})

        link.append(label)
        return link

