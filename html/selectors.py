#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.modeling import ListWrapper, SetWrapper
from cocktail.translations import translate
from cocktail.schema import Number
from cocktail.html import Element
from cocktail.html.checkbox import CheckBox
from cocktail.controllers.viewstate import view_state

class Selector(Element):

    name = None
    items = ()
    value = None
   
    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self._is_selected = lambda item: False

    def _ready(self):

        Element._ready(self)

        if self.member:
        
            if self.name is None and self.member.name:
                self.name = self.member.name

            if self.items is None:
            
                if self.member.enumeration:
                    self.items = self.member.enumeration

                elif isinstance(self.member, Number) \
                and self.member.min and self.member.max:
                    self.items = range(self.member.min, self.member.max + 1)
            
        self._fill_entries()

    def _fill_entries(self):
        
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
        return str(item)

    def get_item_label(self, item):
        return translate(item, default = unicode(item))
    
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

class DropdownSelector(Selector):

    tag = "select"

    def create_entry(self, value, label, selected):
        entry = Element("option")
        entry["value"] = value
        entry["selected"] = selected
        entry.append(label)
        return entry

    def _get_name(self):
        return self["name"]

    def _set_name(self, value):
        self["name"] = value

    name = property(_get_name, _set_name, doc = """
        Gets or sets the name that the selector will take in HTML forms.
        @type: str
        """)


class RadioSelector(Selector):

    def create_entry(self, value, label, selected):
        entry = Element("input")
        entry["type"] = "radio"
        entry["value"] = value
        entry["selected"] = selected        
        entry["name"] = self.name
        entry.append(label)
        return entry


class LinkSelector(Selector):

    def create_entry(self, value, label, selected):
        
        entry = Element()

        if selected:
            entry.add_class("selected")

        link = Element("a")
        link["href"] = "?" + view_state(**{self.name: value})
        link.append(label)
        entry.append(link)

        return entry


class CheckList(Selector):

    def create_entry(self, value, label, selected):

        entry = Element()
        entry_id = self.name + "-" + value

        entry.check = CheckBox()
        entry.check["name"] = self.name
        entry.check["id"] = entry_id
        entry.check.value = selected
        entry.check["value"] = value
        entry.append(entry.check)

        entry.label = Element("label")
        entry.label["for"] = entry_id
        entry.label.append(label)
        entry.append(entry.label)

        return entry

