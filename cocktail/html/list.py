#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from itertools import islice
from cocktail.html import Element
from cocktail.translations import translations


class List(Element):

    tag = "ul"
    max_length = None
    items = None

    def _ready(self):
        Element._ready(self)
        self._fill_entries()

    def _fill_entries(self):

        ellipsis = 0
        items = self.items

        if items:
            if self.max_length:
                ellipsis = len(items) - self.max_length
                if ellipsis > 0:
                    items = islice(items, 0, self.max_length)

            for item in items:
                self.append(self.create_entry(item))

            if ellipsis > 0:
                self.append(self.create_ellipsis(ellipsis))

    def create_entry(self, item):
        entry = Element("li")
        entry.append(self.create_entry_content(item))
        return entry
    
    def create_entry_content(self, item):
        return translations(item, default = item)
    
    def create_ellipsis(self, ellipsis_size):
        ellipsis = Element("span")
        ellipsis.append(translations("List ellipsis", size = ellipsis_size))
        return ellipsis

