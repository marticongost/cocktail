#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
"""
from __future__ import with_statement
from cocktail import schema
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
    grouped = True

    def __init__(self, *args, **kwargs):
        DataDisplay.__init__(self)
        Element.__init__(self, *args, **kwargs)
        self.__flattened_members = {}

    def _ready(self):
        Element._ready(self)

        if self.grouped:
            for group, members in self.displayed_members_by_group:
                tbody = self.create_group(group, members)
                if group:
                    setattr(self, group + "_group", tbody)
                self.append(tbody)
        else:
            self._create_rows(self.displayed_members, self)

    def should_flatten(self, member):
        if isinstance(member, schema.BaseDateTime):
            return False
        member = self._normalize_member(member)
        return self.__flattened_members.get(member, True)

    def set_should_flatten_member(self, member, flattened):
        member = self._normalize_member(member)
        self.__flattened_members[member] = flattened

    def _flatten_members(self, members):
        for member in members:
            if isinstance(member, schema.Schema) \
            and self.should_flatten(member):
                for descendant \
                in self._flatten_members(member.ordered_members()):
                    yield descendant
            else:
                yield member

    def create_group(self, group, members):
        tbody = Element("tbody")

        if group:
            tbody.add_class(group.replace(".", "_") + "_group")
            tbody.header_row = self.create_group_header(group)
            if tbody.header_row:
                tbody.append(tbody.header_row)

        self._create_rows(members, tbody)
        return tbody

    def create_group_header(self, group):
        label = self.get_group_label(group)
        if label:
            row = Element("tr")
            row.add_class("group_header")
            th = Element("th")
            th["colspan"] = 2
            th.append(label)
            row.header = th
            row.append(th)
            return row

    def _create_rows(self, members, container):
        members = self._flatten_members(members)
        for i, member in enumerate(members):
            member_row = self.create_member_row(member)
            member_row.add_class("even" if i % 2 else "odd")
            setattr(self, member.name + "_member", member_row)
            container.append(member_row)

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
        cell.append(
            self.create_member_display(
                self.data,
                member,
                self.get_member_value(self.data, member)
            )
        )
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

