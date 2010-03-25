#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
"""
from __future__ import with_statement
from cocktail.html.element import Element
from cocktail.html.datadisplay import DataDisplay
from cocktail.translations import (
    translations,
    get_language,
    language_context
)


class PropertyTable(Element, DataDisplay):

    tag = "table"
    translations = None

    def __init__(self, *args, **kwargs):
        DataDisplay.__init__(self)
        Element.__init__(self, *args, **kwargs)

    def _ready(self):
        Element._ready(self)

        for group, members in self.displayed_members_by_group:
            tbody = self.create_group(group, members)
            if group:
                setattr(self, group + "_group", tbody)
            self.append(tbody)

    def create_group(self, group, members):
        tbody = Element("tbody")
        
        if group:
            tbody.add_class(group + "_group")
            tbody.header_row = self.create_group_header(group)
            tbody.append(tbody.header_row)
        
        for i, member in enumerate(members):            
            member_row = self.create_member_row(member)
            member_row.add_class("even" if i % 2 else "odd")
            setattr(self, member.name + "_member", member_row)
            tbody.append(member_row)

        return tbody

    def create_group_header(self, group):
        row = Element("tr")
        row.add_class("group_header")
        th = Element("th")
        th["colspan"] = 2
        th.append(self.get_group_label(group))
        row.append(th)
        return row
    
    def create_member_row(self, member):

        row = Element("tr")
        row.add_class("member_row")
        row.add_class(member.name + "_member")
        
        label = self.create_label(member)
        row.append(label)

        if member.translated:
            row.add_class("translated")
            row.append(self.create_translated_values(member))
        else:
            row.append(self.create_value(member))

        return row

    def create_label(self, member):
        label = Element("th")
        label.append(self.get_member_label(member))
        return label

    def create_value(self, member):
        cell = Element("td")
        cell.append(self.get_member_display(self.data, member))
        return cell
        
    def create_translated_values(self, member):
        cell = Element("td")

        table = Element("table")
        table.add_class("translated_values")
        cell.append(table)
        
        for language in (self.translations or (get_language(),)):

            language_row = Element("tr")
            language_row.add_class(language)
            table.append(language_row)

            language_label = Element("th")
            language_label.append(translations(language))
            language_row.append(language_label)
            
            with language_context(language):
                language_value_cell = self.create_value(member)
                
            language_row.append(language_value_cell)            

        return cell

