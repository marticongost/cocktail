#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import get_language
from cocktail.html import Element, TranslatedValue, templates


class MappingTable(Element):

    tag = "table"
    value = None
    sorted = True
    default_display = TranslatedValue

    def _ready(self):
        if self.value and self.member:

            if self.sorted:
                items = self.value.items()
                items.sort()
            else:
                items = self.value.iteritems()

            for key, value in items:
                row = self.create_row(key, value)
                self.append(row)

    def create_row(self, key, value):
        row = Element("tr")
        row.key_cell = self.create_key_cell(key)
        row.append(row.key_cell)
        row.value_cell = self.create_value_cell(value)
        row.append(row.value_cell)
        return row

    def create_key_cell(self, key):
        key_cell = Element("th")
        key_cell.display = self._get_display(self.member.keys, key)
        key_cell.append(key_cell.display)
        return key_cell

    def create_value_cell(self, value):
        value_cell = Element("td")
        value_cell.display = self._get_display(self.member.values, value)
        value_cell.append(value_cell.display)
        return value_cell

    def _get_display(self, member, value):

        display = member and member.display or self.default_display

        if isinstance(display, type) and issubclass(display, Element):
            display = display()
        elif callable(display):
            if getattr(display, "im_self", None) is self:
                display = display(self.value, member)
            else:
                display = display(self, self.value, member)

        if isinstance(display, basestring):
            display = templates.new(display)

        display.data_display = self
        display.data = self.value
        display.member = member
        display.language = get_language()

        if hasattr(display, "value"):
            display.value = value

        return display

