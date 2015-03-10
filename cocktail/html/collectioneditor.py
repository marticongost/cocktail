#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import get_language
from cocktail.html.element import Element
from cocktail.html import templates


class CollectionEditor(Element):

    def _build(self):
        self.add_resource("/cocktail/scripts/CollectionEditor.js")
        self.entries = self.create_entries()
        self.append(self.entries)
        self.add_button = self.create_add_button()
        self.append(self.add_button)

    def _ready(self):
        if self.member:
            self.new_entry = self.create_new_entry()
            self.append(self.new_entry)

            if self.value is not None:
                for item in self.value:
                    self.entries.append(self.create_entry(item))

    def create_entries(self):
        entries = Element()
        entries.add_class("entries")
        return entries

    def create_entry(self, item):
        entry = Element()
        entry.add_class("entry")
        entry.control = self.create_control(item)
        entry.append(entry.control)
        entry.remove_button = self.create_remove_button(item)
        entry.append(entry.remove_button)
        return entry

    def create_remove_button(self, item):
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
        default_value = self.member.items.produce_default()
        new_entry = self.create_entry(default_value)
        new_entry.client_model = \
            "cocktail.html.CollectionEditor.new_entry-" + self.require_id()
        return new_entry

    def create_control(self, item):
        return self.ui_generator.create_member_display(
            self.value,
            self.member.items,
            item,
            collection = self.member
        )

