#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2009
"""
from cocktail.html import Element
from cocktail.html.selector import Selector
from cocktail.html.datadisplay import (
    SINGLE_SELECTION,
    MULTIPLE_SELECTION
)

uneligible = object()


class TreeSelector(Selector):

    tag = "ul"
    selection_mode = SINGLE_SELECTION
    children_collection = "children"
    eligible_folders = True

    def _ready(self):

        if self.selection_mode == MULTIPLE_SELECTION:
            self.empty_option_displayed = False

        if not self.name and self.data_display:
            self.name = self.data_display.get_member_name(
                self.member,
                self.language
            )

        Selector._ready(self)

    def get_item_value(self, item):
        if not self.eligible_folders and self.get_child_items(item):
            return uneligible

        return Selector.get_item_value(self, item)

    def get_child_items(self, item):
        return getattr(item, self.children_collection, None) or ()

    def _fill_entries(self):

        if self.empty_option_displayed:
            entry = self.create_entry(
                self.empty_value,
                self.empty_label,
                self.value is None
            )
            self.append(entry)

        if self.items:
            self._fill_container(self, self.items)

    def _fill_container(self, container, items):

        for item in items:
            value = self.get_item_value(item)
            label = self.get_item_label(item)
            entry = self.create_entry(
                value,
                label,
                self._is_selected(value)
            )

            children = self.get_child_items(item)
            if children:
                children_container = Element("ul")
                self._fill_container(children_container, children)
                entry.append(children_container)

            container.append(entry)

    def create_entry(self, value, label, selected):

        entry = Element("li")
        eligible = value is not uneligible

        # Control (checkbox or radio button)
        if eligible:
            entry.control = Element("input",
                name = self.name,
                value = value,
                checked = selected
            )

            if self.selection_mode == SINGLE_SELECTION:
                entry.control["type"] = "radio"

            elif self.selection_mode == MULTIPLE_SELECTION:
                entry.control["type"] = "checkbox"

            entry.append(entry.control)

        # Label
        if eligible:
            entry.label = Element("label")
            entry.label["for"] = entry.control.require_id()
        else:
            entry.label = Element("span")
            entry.add_class("uneligible")

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

