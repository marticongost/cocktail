#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from collections import Counter
from cocktail.translations import get_language
from cocktail.html import Element, TranslatedValue, templates


class MappingTable(Element):

    tag = "table"
    sorted = True

    def _ready(self):
        if self.value and self.member:

            if isinstance(self.value, Counter):
                items = self.value.most_common()
            elif self.sorted:
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
        key_cell.display = self.ui_generator.create_member_display(
            self.value,
            self.member.keys,
            key
        )
        key_cell.append(key_cell.display)
        return key_cell

    def create_value_cell(self, value):
        value_cell = Element("td")
        value_cell.display = self.ui_generator.create_member_display(
            self.value,
            self.member.values,
            value
        )
        value_cell.append(value_cell.display)
        return value_cell

