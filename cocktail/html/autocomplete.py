#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html import Element
from cocktail.html.textbox import TextBox
from cocktail.html.databoundcontrol import delegate_control


class Autocomplete(Element):

    value = None
    autocomplete_source = None
    autocomplete_entries = None
    autocomplete_delay = 150
    narrow_down = True
    highlighting = True
    auto_select = False
    allow_full_list = True

    def _build(self):
        self.add_resource("/cocktail/styles/Autocomplete.css")
        self.add_resource("/cocktail/scripts/xregexp.js")
        self.add_resource("/cocktail/scripts/searchable.js")
        self.add_resource("/cocktail/scripts/Autocomplete.js")
        self.text_box = self.create_text_box()
        self.append(self.text_box)
        delegate_control(self, self.text_box)

    def create_text_box(self):
        text_box = TextBox()
        text_box.add_class("text_box")
        return text_box

    def _ready(self):

        entries = self.autocomplete_entries

        if entries is None:
            if isinstance(self.autocomplete_source, basestring):
                self.set_client_param(
                    "autocompleteSource",
                    self.autocomplete_source
                )
            else:
                source = self.autocomplete_source
                if source is None and self.member:
                    source = self.member.get_possible_values()

                if source is not None:
                    entries = [
                        self.get_autocomplete_entry(item)
                        for item in source
                    ]

        if entries is not None:
            self.set_client_param("autocompleteSource", entries)

        self.set_client_param("autocompleteDelay", self.autocomplete_delay)
        self.set_client_param("narrowDown", self.narrow_down)
        self.set_client_param("highlighting", self.highlighting)
        self.set_client_param("autoSelect", self.auto_select)
        self.set_client_param("allowFullList", self.allow_full_list)

        if self.value is not None:
            self.set_client_param(
                "selectedEntry",
                self.get_autocomplete_entry(self.value)
            )

    def get_autocomplete_entry(self, item):
        return {
            "value": self.get_entry_value(item),
            "label": self.get_entry_label(item)
        }

    def get_entry_value(self, item):
        return self.member.serialize_request_value(item)

    def get_entry_label(self, item):
        return self.member.translate_value(item)

