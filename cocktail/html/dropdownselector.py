#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html.element import Element
from cocktail.html.selector import Selector


class DropdownSelector(Selector):

    tag = "select"

    def create_group(self, group):
        container = Element("optgroup")
        container["label"] = self.get_group_title(group)
        self._create_entries(group.items, container)

        if group.groups:
            raise ValueError(
                "Can't display nested groups usign a <select> control; "
                "The HTML standard forbids nested <optgroup> elements."
            )

        self._create_nested_groups(group, container)
        return container

    def create_entry(self, item):
        entry = Element("option")
        entry["value"] = self.get_item_value(item)
        entry["selected"] = self.is_selected(item)
        entry.append(self.get_item_label(item))
        return entry

