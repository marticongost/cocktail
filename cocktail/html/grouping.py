#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.styled import styled
from cocktail.modeling import frozen
from cocktail.stringutils import normalize
from cocktail.sortedcollection import SortedCollection
from cocktail.translations import translations

no_key = object()


class Grouping(object):

    grouping = None
    sorted = True
    prefilled = False
    sort_groups_alphabetically = True

    def __init__(self, key = None, sorted = None, prefilled = None):
        self.key = key
        self.sorted = self.sorted if sorted is None else sorted
        self.prefilled = self.prefilled if prefilled is None else prefilled

        if self.sorted:
            self.__items = SortedCollection(
                key = self.get_item_sorting_key
            )
            self.__group_list = SortedCollection(
                key = self.get_group_sorting_key
            )
        else:
            self.__items = []
            self.__group_list = []

        self.__parent_group = None
        self.__group_map = {}

    def __repr__(self):
        return "%s(key = %r)" % (self.__class__.__name__, self.key)

    def __translate__(self, language, **kwargs):

        if self.__parent_group:
            parent_translation = self.__parent_group.get_child_group_label(
                self,
                language,
                **kwargs
            )
            if parent_translation:
                return parent_translation

        return self.get_group_label(language, **kwargs)

    def get_group_label(self, language, **kwargs):
        return translations(self.key, language)

    def get_child_group_label(self, group, language, **kwargs):
        return None

    @classmethod
    def init_element(cls, element):

        grouping = element.grouping

        if grouping is not None:
            element["cocktail-grouping"] = "true"

            if isinstance(grouping, type):
                element.grouping = grouping = grouping()

            if not grouping.prefilled:
                items = getattr(element, "items", None)
                if items:
                    grouping.populate(items)
        else:
            element["cocktail-grouping"] = "false"

    @property
    def items(self):
        return self.__items

    def add_item(self, item):
        if self.sorted:
            self.__items.insert(item)
        else:
            self.__items.append(item)

    @property
    def groups(self):
        return self.__group_list

    def add_group(self, group):

        if group.__parent_group:
            raise ValueError("Groups can't be relocated")

        if group.key in self.__group_map:
            raise ValueError(
                "Can't add %r to %r: it already contains a child group with "
                "that value"
            )

        group.__parent_group = self

        if self.sorted:
            self.__group_list.insert(group)
        else:
            self.__group_list.append(group)

        self.__group_map[group.key] = group

    def get_item_key(self, item):
        return no_key

    def get_item_sorting_key(self, item):
        return normalize(translations(item))

    def get_group_sorting_key(self, grouping):
        if self.sort_groups_alphabetically:
            return normalize(translations(grouping))
        else:
            return grouping.key

    def find_group(self, item):

        key = self.get_item_key(item)

        if key is no_key:
            return self
        else:
            child = self.__group_map.get(key)
            if child is None:
                return None
            else:
                return child.find_group(item)

    def request_group(self, item):

        key = self.get_item_key(item)

        if key is no_key:
            return self
        else:
            child = self.__group_map.get(key)
            if child is None:
                child = self.create_group(key)
                self.add_group(child)
            return child.request_group(item)

    def create_group(self, key):
        return (self.grouping or Grouping)(key = key)

    def populate(self, items):
        for item in items:
            group = self.request_group(item)
            group.add_item(item)

    def print_tree(self, indent = ""):
        print indent + styled(repr(self), "slate_blue")
        indent += "  "
        for group in self.groups:
            group.print_tree(indent)
        for item in self.items:
            print indent + styled(item, "pink")


class GroupByMember(Grouping):

    member = None

    def __init__(self, member = None, **kwargs):
        Grouping.__init__(self, **kwargs)
        self.member = member or self.member

    def __repr__(self):
        return "%s(member = %r, key = %r)" % (
            self.__class__.__name__,
            self.member,
            self.key
        )

    def get_child_group_label(self, group, language, **kwargs):
        return self.member.translate_value(
            group.key,
            language = language
        )

    def get_item_key(self, item):
        value = item.get(self.member)
        return frozen(value)

    def get_sorting_key(self):
        return normalize(translations(self))

