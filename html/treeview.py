#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.translations import translate
from cocktail.html import Element


class TreeView(Element):

    tag = "ul"
    root = None
    root_visible = True

    def _ready(self):
        if self.root is not None:
            if self.root_visible:
                self.root_entry = self.create_entry(self.root)
                self.append(self.root_entry)
            else:
                self._fill_children_container(
                    self,
                    self.root,
                    self.get_child_items(self.root)
                )                

    def create_entry(self, item):
        
        entry = Element("li")
    
        entry.label = self.create_label(item)
        entry.append(entry.label)

        children = self.get_child_items(item)

        if children:
            entry.container = self.create_children_container(item, children)
            entry.append(entry.container)

        return entry

    def create_label(self, item):
        label = Element("div")
        label.add_class("entry_label")
        label.append(self.get_item_label(item))
        return label

    def get_item_label(self, item):
        return translate(item)

    def create_children_container(self, item, children):        
        container = Element("ul")
        self._fill_children_container(container, item, children)
        return container

    def _fill_children_container(self, container, item, children):
        for child in children:
            container.append(self.create_entry(child))

    def get_child_items(self, parent):
        return parent.children

