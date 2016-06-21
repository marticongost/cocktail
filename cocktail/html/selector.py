#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.modeling import ListWrapper, SetWrapper, OrderedDict
from cocktail.translations import translations
from cocktail import schema
from cocktail.schema import ValidationContext
from cocktail.persistence import PersistentObject
from cocktail.html import Element
from cocktail.html.grouping import Grouping
from cocktail.controllers.parameters import serialize_parameter


class Selector(Element):

    is_form_control = True
    items = None
    groups = None
    persistent_object = None

    empty_option_displayed = True
    empty_value = ""
    empty_label = None
    grouping = None

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self._is_selected = lambda item: False

    def _ready(self):

        Element._ready(self)
        item_translator = None

        if self.member:

            if self.items is None and self.groups is None:
                self.items = self._get_items_from_member(self.member)

            if isinstance(self.member, schema.Collection):
                if self.member.items:
                    item_translator = self.member.items.translate_value
            else:
                item_translator = self.member.translate_value

        self._item_translator = (
            item_translator
            or (lambda item, **kw: translations(item, **kw))
        )

        Grouping.init_element(self)

        if self.value is None:
            self._is_selected = lambda item: item is None
        elif (
            isinstance(
                self.value,
                (list, tuple, set, ListWrapper, SetWrapper)
            )
            and not isinstance(self.member, schema.Tuple)
        ):
            self._is_selected = lambda item: item in self.value
        else:
            self._is_selected = lambda item: item == self.value

        self._fill_entries()

    def _get_items_from_member(self, member):

        if isinstance(member, schema.Collection):
            member = member.items

        if (
            self.ui_generator
            and self.ui_generator.schema
            and self.ui_generator.data
        ):
            parent_context = ValidationContext(
                self.ui_generator.schema,
                self.ui_generator.data
            )
        else:
            parent_context = None

        context = ValidationContext(
            member,
            self.value,
            persistent_object = self.persistent_object,
            parent_context = parent_context
        )

        return member.get_possible_values(context)

    def _fill_entries(self):

        if self.empty_option_displayed:
            entry = self.create_entry(None)
            self.append(entry)

        if self.grouping is not None:
            for grouping in self.grouping.groups:
                self.append(self.create_group(grouping))
            self._create_entries(self.grouping.items, self)
        elif self.items is not None:
            self._create_entries(self.items, self)

    def _create_entries(self, items, container):
        for item in items:
            entry = self.create_entry(item)
            container.append(entry)

    def get_item_value(self, item):

        if item is None and self.empty_value is not None:
            return self.empty_value

        member = (
            self.member
            and (
                isinstance(self.member, schema.Collection)
                and self.member.items
            )
            or self.member
        )

        if member:
            try:
                return serialize_parameter(member, item)
            except:
                pass

        return getattr(item, "id", None) or str(item)

    def get_item_label(self, item):

        if item is None:
            empty_label = self.empty_label

            if not empty_label and self.member:
                empty_label = self.member.translate_value(None)

            if not empty_label:
                empty_label = "---"

            return empty_label

        return self._item_translator(item)

    def is_selected(self, item):
        return self._is_selected(item)

    def create_group(self, grouping):

        container = Element()
        container.add_class("group")

        container.label = self.create_group_label(grouping)
        container.append(container.label)

        self._create_entries(grouping.items, container)
        self._create_nested_groups(grouping, container)

        return container

    def _create_nested_groups(self, grouping, container):
        for nested_group in grouping.groups:
            container.append(self.create_group(nested_group))

    def create_group_label(self, grouping):
        label = Element()
        label.add_class("group_label")
        label.append(self.get_group_title(grouping))
        return label

    def get_group_title(self, grouping):
        return translations(grouping)

    def create_entry(self, item):
        raise TypeError(
            "%s doesn't implement the create_entry() method" % self
        )

