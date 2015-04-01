#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html import Element
from cocktail.html.textbox import TextBox
from cocktail.controllers.autocomplete import MemberAutocompleteSource


class Autocomplete(Element):

    autocomplete_source = None
    autocomplete_entries = None
    autocomplete_delay = 150
    ajax_search = False
    ajax_search_threshold = None
    ajax_url = None

    # Client side settings
    narrow_down = True
    highlighting = True
    auto_select = False
    allow_full_list = True
    auto_expand = False
    select_text_on_focus = True

    def _build(self):
        self.add_resource("/cocktail/styles/Autocomplete.css")
        self.add_resource("/cocktail/scripts/xregexp.js")
        self.add_resource("/cocktail/scripts/searchable.js")
        self.add_resource("/cocktail/scripts/Autocomplete.js")
        self.text_box = self.create_text_box()
        self.append(self.text_box)
        self.data_binding_delegate = self.text_box

    def create_text_box(self):
        text_box = TextBox()
        text_box.add_class("text_box")
        return text_box

    def _ready(self):

        if self.autocomplete_source is None and self.member:
            self.autocomplete_source = self.create_autocomplete_source()

        entries = self.autocomplete_entries

        if entries is None:
            if (
                self.ajax_search
                and (
                    self.ajax_search_threshold is None
                    or len(self.autocomplete_source.items) >= self.ajax_search_threshold
                )
            ):
                ajax_url = self.ajax_url or self.get_default_ajax_url()
            else:
                ajax_url = None

            if ajax_url:
                self.set_client_param("autocompleteSource", ajax_url)
            elif self.autocomplete_source is not None:
                entries = [
                    self.autocomplete_source.get_entry(item)
                    for item in self.autocomplete_source.items
                ]

        if entries is not None:
            self.set_client_param("autocompleteSource", entries)

        self.set_client_param("autocompleteDelay", self.autocomplete_delay)
        self.set_client_param("narrowDown", self.narrow_down)
        self.set_client_param("highlighting", self.highlighting)
        self.set_client_param("autoSelect", self.auto_select)
        self.set_client_param(
            "allowFullList",
            self.allow_full_list or self.auto_expand
        )
        self.set_client_param("selectTextOnFocus", self.select_text_on_focus)
        self.set_client_param("autoExpand", self.auto_expand)

        if self.value is not None and self.autocomplete_source is not None:
            self.set_client_param(
                "selectedEntry",
                self.autocomplete_source.get_entry(self.value)
            )

    def create_autocomplete_source(self):
        return MemberAutocompleteSource(self.member)

    def get_default_ajax_url(self):
        return None

