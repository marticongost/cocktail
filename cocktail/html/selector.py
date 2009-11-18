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
from cocktail.html import Element
from cocktail.html.databoundcontrol import DataBoundControl


class Selector(Element, DataBoundControl):

    name = None
    items = None
    __value = None
    
    empty_option_displayed = True
    empty_value = ""
    empty_label = "---"
   
    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        DataBoundControl.__init__(self)
        self._is_selected = lambda item: False

    def _ready(self):

        Element._ready(self)
        item_translator = None

        if self.member:
        
            if self.items is None:
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
        
        self._fill_entries()

    def _get_items_from_member(self, member):
        
        if isinstance(member, schema.Collection):
            enumeration = member.items.enumeration if member.items else None
        else:
            enumeration = member.enumeration
        
        if enumeration is not None:
            enumeration = member.resolve_constraint(enumeration, None)
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
                    items.add_order(order)

                return items
                
            elif isinstance(member, schema.Collection):
                if member.items:
                    return self._get_items_from_member(member.items)
        
        return ()

    def _fill_entries(self):
        
        if self.empty_option_displayed:
            entry = self.create_entry(
                self.empty_value,
                self.empty_label,
                self.value is None
            )
            self.append(entry)

        if hasattr(self.items, "iteritems"):
            for value, label in self.items.iteritems():
                value = self.get_item_value(value)
                entry = self.create_entry(
                    value,
                    label,
                    self._is_selected(value)
                )
                self.append(entry)
        else:
            for item in self.items:
                value = self.get_item_value(item)
                label = self.get_item_label(item)
                entry = self.create_entry(
                    value,
                    label,
                    self._is_selected(value)
                )
                self.append(entry)
    
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

