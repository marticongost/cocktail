#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from warnings import warn
from cocktail.translations import translations
from cocktail.html import Element

NOT_ACCESSIBLE = 0
ACCESSIBLE = 1
ACCESSIBLE_DESCENDANTS = 2


class TreeView(Element):

    HIDDEN_ROOT = 0
    SINGLE_ROOT = 1
    MERGED_ROOT = 2
    ITERABLE_ROOT = 3

    tag = "ul"
    root = None
    root_visibility = SINGLE_ROOT
    selection = None
    expanded = True
    max_depth = None
    create_empty_containers = False
    display_filtered_containers = True
    filter_item = None
    __item_access = None

    def _get_root_visible(self):
        return self.root_visibility not in (
            self.HIDDEN_ROOT,
            self.ITERABLE_ROOT
        )

    def _set_root_visible(self, value):
        warn(
            "The cocktail.html.TreeView.root_visible property has been "
            "deprecated in favor of cocktail.html.TreeView.root_visibility",
            DeprecationWarning,
            stacklevel = 2
        )
        self.root_visibility = self.SINGLE_ROOT if value else self.HIDDEN_ROOT

    root_visible = property(_get_root_visible, _set_root_visible)

    def _is_accessible(self, item, depth = None):
        
        if self.__item_access is None:
            self.__item_access = {}
        
        accessibility = self.__item_access.get(item)

        if accessibility is None:

            if depth is None:
                depth = 0
                node = item
                while node is not None:
                    depth += 1
                    node = self.get_parent_item(node)

            if self.filter_item(item):
                accessibility = ACCESSIBLE
            elif (self.max_depth is None or self.max_depth > depth) and any(
                self._is_accessible(child, depth + 1)
                for child in self.get_child_items(item)
            ):
                accessibility = ACCESSIBLE_DESCENDANTS
            else:
                accessibility = NOT_ACCESSIBLE

            self.__item_access[item] = accessibility

        return accessibility

    def _ready(self):

        Element._ready(self)
 
        # Find the selected path
        self._expanded = set()
        item = self.selection

        while item is not None:
            self._expanded.add(item)
            item = self.get_parent_item(item)

        if self.root is not None:
            if self.root_visibility == self.SINGLE_ROOT:
                self._depth = 2
                if not self.filter_item or self._is_accessible(self.root):
                    self.root_entry = self.create_entry(self.root)
                    self.append(self.root_entry)
            else:
                self._depth = 1

                if self.root_visibility == self.ITERABLE_ROOT:
                    children = self.root
                else:
                    children = self.get_expanded_children(self.root)

                if self.root_visibility == self.MERGED_ROOT:
                    children = [self.root] + list(children)

                self._fill_children_container(
                    self,
                    self.root,
                    children
                )

        self.__item_access = None

    def create_entry(self, item):
        
        entry = Element("li")
 
        if (
            not (
                self.root_visibility == self.MERGED_ROOT 
                and item is self.root
                and self.selection is not self.root
            )
            and item in self._expanded
        ):
            entry.add_class("selected")

        entry.label = self.create_label(item)
        entry.append(entry.label)

        children = self.get_expanded_children(item)

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
        self._depth += 1

        if children:
            for child in children:
                if self.filter_item:
                    accessibility = self._is_accessible(
                        child, 
                        depth = self._depth
                    )
                    if accessibility == NOT_ACCESSIBLE or (
                        accessibility == ACCESSIBLE_DESCENDANTS
                        and not self.display_filtered_containers
                    ):
                        continue

                container.append(self.create_entry(child))

        self._depth -= 1

    def get_parent_item(self, item):
        return getattr(item, "parent", None)
  
    def get_child_items(self, parent):
        return getattr(parent, "children", [])

    def get_item_url(self, content_type):
        return None

    def get_expanded_children(self, parent):
        if self.should_collapse(parent):
            return []
        else:
            return self.get_child_items(parent)

    def should_collapse(self, parent):        
        return (
            (self.max_depth is not None and self._depth > self.max_depth)
            or (
                self.root_visibility == self.MERGED_ROOT 
                and parent is self.root
                and self._depth > 1
            )
            or (not self.expanded and parent not in self._expanded)
        )

