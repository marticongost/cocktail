#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html import Element, templates
from cocktail.html.selector import Selector

CheckBox = templates.get_class("cocktail.html.CheckBox")


class CheckList(Selector):

    empty_option_displayed = False
    column_count = None
    column_height = None

    def _ready(self):

        if not self.name and self.data_display:
            self.name = self.data_display.get_member_name(
                self.member,
                self.language
            )

        Selector._ready(self)
 
    def _create_entries(self, items, container):
        if self.column_count is None and self.column_height is None:
            Selector._create_entries(self, items, container)
        else:
            self.add_class("with_columns")
            pairs = list(self._iter_pairs(items))

            if self.column_height:
                column_height = self.column_height
                remainder = 0
            else:
                column_height, remainder = divmod(len(pairs), self.column_count)
                if remainder:
                    column_height += 1

            column = None

            for i, (value, label) in enumerate(pairs):
                
                if column is None or not column.capacity:

                    column = self.create_column()
                    column.capacity = column_height

                    if remainder:
                        remainder -= 1
                        if not remainder:
                            column_height -= 1

                    container.append(column)

                entry = self.create_entry(
                    value,
                    label,
                    self._is_selected(value)
                )

                column.append(entry)
                column.capacity -= 1

    def create_column(self):
        column = Element()
        column.add_class("column")
        return column

    def create_entry(self, value, label, selected):

        entry = Element()

        entry.check = CheckBox()
        entry.check["name"] = self.name
        entry.check.value = selected
        entry.check["value"] = value
        entry.append(entry.check)

        entry.label = Element("label")
        entry.label["for"] = entry.check.require_id()
        entry.label.append(label)
        entry.append(entry.label)

        return entry

    def insert_into_form(self, form, field_instance):
        
        field_instance.append(self)

        # Disable the 'required' mark for this field, as it doesn't make sense
        # on a checklist
        required_mark = getattr(field_instance.label, "required_mark", None)

        if required_mark and \
        not (self.member and \
        self.member.min and \
        isinstance(self.member.min, int) and \
        self.member.min > 0):
            required_mark.visible = False

