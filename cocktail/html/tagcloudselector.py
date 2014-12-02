#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail.schema import Reference, Collection
from cocktail.html import Element, templates
from cocktail.html.selector import Selector
from cocktail.html.checkbox import CheckBox
from cocktail.html.datadisplay import (
    SINGLE_SELECTION,
    MULTIPLE_SELECTION
)
from cocktail.html.tagcloud import get_tag_cloud_font_sizes


class TagCloudSelector(Selector):

    tags = None
    selection_mode = SINGLE_SELECTION
    tag_assignments_member = None

    def _build(self):
        Element._build(self)
        self.add_resource("/cocktail/scripts/TagCloudSelector.js")

    def _ready(self):

        if self.tag_assignments_member and self.tags is None:
            
            self.tags = {}
            self.items = []
                     
            for tag in self.tag_assignments_member.schema.select():
                self.items.append(tag)
                tag_items = tag.get(self.tag_assignments_member)
                tag_frequency = len(tag_items) if tag_items else 0
                tag_value = self.get_item_value(tag)
                self.tags[tag_value] = tag_frequency

        if self.tags:
            if not self.items:
                self.items = list(self.tags)
            self._font_sizes = get_tag_cloud_font_sizes(self.tags)

        if self.selection_mode == MULTIPLE_SELECTION:
            self.empty_option_displayed = False

        if not self.name and self.data_display:
            self.name = self.data_display.get_member_name(
                self.member,
                self.language
            )

        Selector._ready(self)
    
    def create_entry(self, value, label, selected):

        entry = Element()
        entry.add_class("entry")

        if self.selection_mode == SINGLE_SELECTION:
            entry.control = Element("input", type = "radio", checked = selected)
        elif self.selection_mode == MULTIPLE_SELECTION:
            entry.control = CheckBox()
            entry.control.value = selected
        else:
            raise ValueError("Invalid selection mode")

        entry.control["name"] = self.name
        entry.control["value"] = value
        entry.append(entry.control)

        entry.label = Element("label")
        entry.label["for"] = entry.control.require_id()
        entry.label.append(label)
        entry.append(entry.label)

        if value:
            entry.label.set_style("font-size", str(self._font_sizes[value]) + "%")

        return entry

    def insert_into_form(self, form, field_instance):
        
        field_instance.append(self)

        if self.selection_mode == MULTIPLE_SELECTION:
            # Disable the 'required' mark for this field, as it doesn't make sense
            # on a checklist
            required_mark = getattr(field_instance.label, "required_mark", None)

            if required_mark and \
            not (self.member and \
            self.member.min and \
            isinstance(self.member.min, int) and \
            self.member.min > 0):
                required_mark.visible = False

