#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html.element import Element
from cocktail.html.selector import Selector
from cocktail.controllers.viewstate import view_state


class LinkSelector(Selector):

    empty_option_displayed = False

    def create_entry(self, item):

        entry = Element()
        entry.add_class("entry")

        if self.is_selected(item):
            entry.add_class("selected")

        link = self.create_entry_link(item)
        entry.append(link)
        return entry

    def create_entry_link(self, item):

        link = Element("a")
        link.add_class("entry_link")
        link["href"] = self.get_entry_url(item)
        link.append(self.get_item_label(item))
        return link

    def get_entry_url(self, item):

        if self.name:
            name = self.name

            # Ugly hack: view_state uses urlencode(), which can't take unicode
            # strings
            if isinstance(name, unicode):
                name = str(name)

            return "?" + view_state(**{name: self.get_item_value(item)})

