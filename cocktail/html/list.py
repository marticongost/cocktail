#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from itertools import islice
from warnings import warn
from cocktail.translations import translations
from cocktail import schema
from cocktail.html import Element
from cocktail.html.uigeneration import UIGenerator, default_display


class List(Element, UIGenerator):

    tag = "ul"
    max_length = None
    base_ui_generators = [default_display]
    sort_key = None

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        UIGenerator.__init__(self)

    def _get_items(self):
        warn(
            "List.items is deprecated, use List.value instead",
            DeprecationWarning,
            stacklevel = 2
        )
        return self.value

    def _set_items(self, items):
        warn(
            "List.items is deprecated, use List.value instead",
            DeprecationWarning,
            stacklevel = 2
        )
        self.value = items

    items = property(_get_items, _set_items)

    def _ready(self):
        Element._ready(self)
        self._fill_entries()

    def _fill_entries(self):

        ellipsis = 0
        items = self.value

        if items:
            if self.sort_key:
                items = list(items)
                items.sort(key = self.sort_key)

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
        if self.member:
            if isinstance(self.member, schema.Mapping):
                if self.member.values:
                    return self.create_member_display(
                        self.data,
                        self.member.values,
                        item
                    )
            elif isinstance(self.member, schema.Collection):
                if self.member.items:
                    return self.create_member_display(
                        self.data,
                        self.member.items,
                        item
                    )

        return translations(item, default = item)

    def create_ellipsis(self, ellipsis_size):
        ellipsis = Element("span")
        ellipsis.append(translations("List ellipsis", size = ellipsis_size))
        return ellipsis

