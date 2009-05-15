#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.translations import translations
from cocktail.html import Element

NOT_ACCESSIBLE = 0
ACCESSIBLE = 1
ACCESSIBLE_DESCENDANTS = 2


class TreeView(Element):

    tag = "ul"
    root = None
    root_visible = True
    create_empty_containers = False
    filter_item = None
    __item_access = None

    def _is_accessible(self, item):
        
        if self.__item_access is None:
            self.__item_access = {}
        
        accessibility = self.__item_access.get(item)

        if accessibility is None:

            if self.filter_item(item):
                accessibility = ACCESSIBLE
            elif any(
                self._is_accessible(child)
                for child in self.get_child_items(item)
            ):
                accessibility = ACCESSIBLE_DESCENDANTS
            else:
                accessibility = NOT_ACCESSIBLE

            self.__item_access[item] = accessibility

        return accessibility

    def _ready(self):
        Element._ready(self)
        
        if self.root is not None:
            if self.root_visible:
                if not self.filter_item or self._is_accessible(self.root):
                    self.root_entry = self.create_entry(self.root)
                    self.append(self.root_entry)
            else:
                self._fill_children_container(
                    self,
                    self.root,
                    self.get_child_items(self.root)
                )

        self.__item_access = None

    def create_entry(self, item):
        
        entry = Element("li")
    
        entry.label = self.create_label(item)
        entry.append(entry.label)

        children = self.get_child_items(item)

        if self.create_empty_containers or children:
            entry.container = self.create_children_container(item, children)
            entry.append(entry.container)

        return entry

    def create_label(self, item):
        label = Element("div")
        label.add_class("entry_label")
        label.append(self.get_item_label(item))

        if self.filter_item \
        and self._is_accessible(item) != ACCESSIBLE:
            label.add_class("filtered")
        else:
            url = self.get_item_url(item)
            if url is not None:
                label.tag = "a"
                label["href"] = url

        return label

    def get_item_label(self, item):
        return translations(item)

    def create_children_container(self, item, children):        
        container = Element("ul")
        container.collapsible = True
        self._fill_children_container(container, item, children)
        return container

    def _fill_children_container(self, container, item, children):
        if children:
            for child in children:
                if not self.filter_item or self._is_accessible(child):
                    container.append(self.create_entry(child))

    def get_child_items(self, parent):
        return parent.children
        
    def get_item_url(self, content_type):
        return None

