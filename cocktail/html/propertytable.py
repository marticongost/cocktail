#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
"""
from __future__ import with_statement
from cocktail.html.element import Element
from cocktail.html.datadisplay import DataDisplay
from cocktail.translations import translate
from cocktail.language import get_content_language, content_language_context


class PropertyTable(Element, DataDisplay):

    tag = "table"
    translations = None

    def __init__(self, *args, **kwargs):
        DataDisplay.__init__(self)
        Element.__init__(self, *args, **kwargs)

    def _ready(self):
        Element._ready(self)

        for member in self.displayed_members:
            entry = self.create_entry(member)
            self.append(entry)

    def create_entry(self, member):

        entry = Element("tr")
        entry.add_class("%s_entry" % member.name)

        label = self.create_label(member)
        entry.append(label)

        if member.translated:
            entry.add_class("translated")
            entry.append(self.create_translated_values(member))
        else:
            entry.append(self.create_value(member))

        return entry

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
        
        for language in (self.translations or (get_content_language(),)):

            language_row = Element("tr")
            language_row.add_class(language)
            table.append(language_row)

            language_label = Element("th")
            language_label.append(translate(language))
            language_row.append(language_label)
            
            with content_language_context(language):
                language_value_cell = self.create_value(member)
                
            language_row.append(language_value_cell)            

        return cell
        
        raise ValueError("Not implemented")

