#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.modeling import ListWrapper, SetWrapper
from cocktail.translations import translations
from cocktail import schema
from cocktail.schema import ValidationContext
from cocktail.persistence import PersistentObject
from cocktail.html import Element
from cocktail.html.databoundcontrol import data_bound


class Selector(Element):

    name = None
    items = None
    __value = None
    persistent_object = None
    
    empty_option_displayed = True
    empty_value = ""
    empty_label = None
    grouping = None
    grouped = False
   
    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        data_bound(self)
        self._is_selected = lambda item: False

    def _ready(self):

        Element._ready(self)
        item_translator = None

        if self.member:
        
            if self.items is None:
                self.items = self._get_items_from_member(self.member)

            if self.grouping:
                groups = []
                group_map = {}

                for item in self.items:
                    group = self.grouping(item)
                    group_items = group_map.get(group)

                    if group_items is None:
                        group_items = []
                        groups.append((group, group_items))
                        group_map[group] = group_items

                    group_items.append(item)

                self.grouped = True
                self.items = groups

            if isinstance(self.member, schema.Collection):
                if self.member.items:
                    item_translator = self.member.items.translate_value
            else:
                item_translator = self.member.translate_value
        
        self._item_translator = (
            item_translator
            or (lambda item, **kw: translations(item, **kw))
        )
        
        self._fill_entries()

    def _get_items_from_member(self, member):
        
        if isinstance(member, schema.Collection):
            enumeration = member.items.enumeration if member.items else None
        else:
            enumeration = member.enumeration
        
        if enumeration is not None:
            # Create the validation context
            if isinstance(self.persistent_object, PersistentObject):
                context = ValidationContext(
                    self.persistent_object.__class__, 
                    self.persistent_object,
                    persistent_object = self.persistent_object
                )
            else:
                context = None

            enumeration = member.resolve_constraint(enumeration, context)
            if enumeration is not None:
                return enumeration

        if isinstance(member, schema.Boolean):
            return (True, False)

        elif isinstance(member, schema.Number):
            if member.min is not None and member.max is not None:
                return range(member.min, member.max + 1)

        elif isinstance(member, schema.RelationMember):
            if getattr(member, "is_persistent_relation", False):
                items = member.select_constraint_instances(
                    parent = self.persistent_object or self.data
                )
                
                order = None

                if isinstance(member, schema.Reference):
                    order = member.default_order
                elif isinstance(member, schema.Collection):
                    order = member.items.default_order

                if order:
                    if isinstance(order, (basestring, schema.Member)):
                        items.add_order(order)
                    else:
                        for criteria in order:
                            items.add_order(criteria)

                return items
                
            elif isinstance(member, schema.Collection):
                if member.items:
                    return self._get_items_from_member(member.items)
        
        return ()

    def _fill_entries(self):
        
        if self.empty_option_displayed:

            empty_label = self.empty_label

            if not empty_label and self.member:
                empty_label = self.member.translate_value(None)

            if not empty_label:
                empty_label = "---"

            entry = self.create_entry(
                self.empty_value,
                empty_label,
                self.value is None
            )
            self.append(entry)

        if self.grouped:
            for group, items in self.items:
                self.append(self.create_group(group, items))
        else:
            self._create_entries(self.items, self)

    def _iter_pairs(self, items):
        if hasattr(items, "iteritems"):
            return (
                (self.get_item_value(value), label)
                for value, label in items.iteritems()
            )
        else:
            return (
                (self.get_item_value(item),
                 self.get_item_label(item))
                for item in items
            )
    
    def _create_entries(self, items, container):
        for value, label in self._iter_pairs(items):
            entry = self.create_entry(
                value,
                label,
                self._is_selected(value)
            )
            container.append(entry)

    def get_item_value(self, item):
       
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
                return member.serialize_request_value(item)
            except:
                pass
        
        return getattr(item, "id", None) or str(item)

    def get_item_label(self, item):
        return self._item_translator(item)
    
    def create_group(self, group, items):

        container = Element()
        container.add_class("group")

        container.label = self.create_group_label(group, items)
        container.append(container.label)

        self._create_entries(items, container)

        return container

    def create_group_label(self, group, items):
        label = Element()
        label.add_class("group_label")
        label.append(self.get_group_title(group, items))
        return label

    def get_group_title(self, group, items):
        return translations(group)

    def create_entry(self, value, label, selected):
        pass

    def _get_value(self):
        return self.__value

    def _set_value(self, value):
        self.__value = value

        if value is None:
            self._is_selected = lambda item: False
        elif isinstance(value, (list, tuple, set, ListWrapper, SetWrapper)):
            selection = set(self.get_item_value(item) for item in value)
            self._is_selected = lambda item: item in selection
        else:
            selection = self.get_item_value(value)
            self._is_selected = lambda item: item == selection

    value = property(_get_value, _set_value, doc = """
        Gets or sets the active selection for the selector.
        """)

