#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.html.element import Element
from cocktail.html.datadisplay import DataDisplay


class MappingEditor(Element):

    fixed_entries = False

    def _build(self):
        self.keys_ui_generator = DataDisplay()
        self.values_ui_generator = DataDisplay()
        self.entries = self.create_entries()
        self.append(self.entries)

    def _ready(self):

        if not self.fixed_entries:
            self.add_resource("/cocktail/scripts/MappingEditor.js")

        if self.ui_generator:
            self.keys_ui_generator.base_ui_generators = [self.ui_generator]
            self.values_ui_generator.base_ui_generators = [self.ui_generator]

        if self.member and self.member.keys and self.member.values:
            if not self.fixed_entries:
                self.new_entry = self.create_new_entry()
                self.append(self.new_entry)

            if self.value is not None:
                for key, value in self.value.iteritems():
                    self.entries.append(self.create_entry(key, value))

            if not self.fixed_entries:
                self.add_button = self.create_add_button()
                self.append(self.add_button)

    def create_entries(self):
        entries = Element()
        entries.add_class("entries")
        return entries

    def create_entry(self, key, value):

        entry = Element()
        entry.add_class("entry")

        entry.key_control = self.create_key_control(key, value)
        entry.append(entry.key_control)

        entry.value_control = self.create_value_control(key, value)
        entry.append(entry.value_control)

        if not self.fixed_entries:
            entry.remove_button = self.create_remove_button(key, value)
            entry.append(entry.remove_button)

        return entry

    def create_key_control(self, key, value):
        control = self.keys_ui_generator.create_member_display(
            self.value,
            self.member.keys,
            key
        )
        control.name = self.name + "-keys"
        control.add_class("key_control")
        return control

    def create_value_control(self, key, value):
        control = self.values_ui_generator.create_member_display(
            self.value,
            self.member.values,
            value,
            item_key = key
        )
        control.name = self.name + "-values"
        control.add_class("value_control")
        return control

    def create_remove_button(self, key, value):
        button = Element("button")
        button.add_class("remove_button")
        button["type"] = "button"
        button.append(u"✖")
        return button

    def create_add_button(self):
        button = Element("button")
        button.add_class("add_button")
        button["type"] = "button"
        button.append(u"✚")
        return button

    def create_new_entry(self):
        default_key = self.member.keys.produce_default()
        default_value = self.member.values.produce_default()
        new_entry = self.create_entry(default_key, default_value)
        new_entry.client_model = \
            "cocktail.html.MappingEditor.new_entry-" + self.require_id()
        return new_entry

