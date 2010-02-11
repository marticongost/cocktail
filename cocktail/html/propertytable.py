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
from cocktail.translations import translations
from cocktail.language import get_content_language, content_language_context


class PropertyTable(Element, DataDisplay):

    tag = "table"
    translations = None
    group_by_type = True

    def __init__(self, *args, **kwargs):
        DataDisplay.__init__(self)
        Element.__init__(self, *args, **kwargs)

    def _ready(self):
        Element._ready(self)

        container = self
        prev_schema = None

        if self.group_by_type:

            self.add_resource("/cocktail/scripts/jquery.cookie.js")
            self.add_resource("/cocktail/scripts/PropertyTable.js")

            if self.tag == "table":
                self.tag = "div"

        for index, member in enumerate(self.displayed_members):
            
            current_schema = member.adaptation_source.schema \
                if member.adaptation_source else member.schema

            if self.group_by_type and current_schema is not prev_schema:
                type_table = Element("table")
                type_table.add_class(current_schema.name+"-group")
                type_table.add_class("type_group")
                type_table.set_client_param("groupSchema", current_schema.name)
                self.append(type_table)
                         
                type_header = self.create_type_header(current_schema)
                type_table.append(type_header)

                container = self.create_type_container(current_schema)
                type_table.append(container)
                
            entry = self.create_entry(index, member)
            setattr(self, member.name + "_member", entry)
            container.append(entry)

            prev_schema = current_schema

    def create_type_header(self, schema):
        header = Element("thead")
        header.add_class("type_header")
        cell = Element("th")
        cell["colspan"] = "2"
        cell.append(self.get_type_header_label(schema))
        header.append(cell)
        return header

    def get_type_header_label(self, schema):
        return translations(schema.name)

    def create_type_container(self, schema):
        return Element("tbody")

    def create_entry(self, index, member):

        entry = Element("tr")
        entry.add_class("member_entry")
        entry.add_class("member_%s_entry" % member.name)

        if index % 2 == 0:
            entry.add_class("odd")
        else:
            entry.add_class("even")

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
            language_label.append(translations(language))
            language_row.append(language_label)
            
            with content_language_context(language):
                language_value_cell = self.create_value(member)
                
            language_row.append(language_value_cell)            

        return cell
        
        raise ValueError("Not implemented")

