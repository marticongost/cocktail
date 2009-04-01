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

    def create_entry(self, value, label, selected):
        entry = Element("option")
        entry["value"] = value
        entry["selected"] = selected
        entry.append(label)
        return entry

    def _get_name(self):
        return self["name"]

    def _set_name(self, value):
        self["name"] = value

    name = property(_get_name, _set_name, doc = """
        Gets or sets the name that the selector will take in HTML forms.
        @type: str
        """)

