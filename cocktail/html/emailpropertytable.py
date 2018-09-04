#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html.propertytable import PropertyTable


class EmailPropertyTable(PropertyTable):

    group_header_style = {
        "padding-top": "1em",
        "border-bottom": "1px solid #bbb",
        "text-align": "left",
        "font-size": "1.2em"
    }

    label_style = {
        "padding-top": "0.5em",
        "padding-right": "1em",
        "text-align": "left",
        "vertical-align": "top",
        "color": "#444",
        "font-weight": "normal"
    }

    value_style = {
        "padding-top": "0.5em",
        "text-align": "left",
        "vertical-align": "top"
    }

    add_colon_after_label = True

    def create_group_header(self, group):
        row = PropertyTable.create_group_header(self, group)
        if row:
            row.header.update_style(self.group_header_style)
        return row

    def create_label(self, member):
        label = PropertyTable.create_label(self, member)
        label.update_style(self.label_style)

        if self.add_colon_after_label:
            label.append(":")

        return label

    def create_value(self, member):
        value = PropertyTable.create_value(self, member)
        value.update_style(self.value_style)
        return value

