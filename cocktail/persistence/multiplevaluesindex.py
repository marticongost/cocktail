#-*- coding: utf-8 -*-
"""Defines the `MultipleValuesIndex` class.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from functools import total_ordering
from typing import NamedTuple, Any
from BTrees.OOBTree import OOTreeSet
from cocktail.modeling import overrides
from .index import Index, Descending, undefined

upper_bound = object()
lower_bound = object()


class MultipleValuesIndex(Index):
    """An `index <Index>` where keys may be defined multiple times."""

    accepts_multiple_values = True

    @overrides(Index.__init__)
    def __init__(self, pairs = None):
        self.__items = OOTreeSet()
        self.__descending_items = OOTreeSet()
        Index.__init__(self, pairs)

    @overrides(Index.add)
    def add(self, key, value):
        self.__items.insert(Entry(key, value))
        self.__descending_items.insert(DescEntry(key, value))

    @overrides(Index.remove)
    def remove(self, key, value = undefined):

        entry = Entry(key, value)
        desc_entry = DescEntry(key, value)

        # Remove all values for the given key
        if value is undefined:
            while True:
                try:
                    self.__items.remove(entry)
                    self.__descending_items.remove(desc_entry)
                except KeyError:
                    break
        # Remove a specific value for the given key
        else:
            try:
                self.__items.remove(entry)
                self.__descending_items.remove(desc_entry)
            except KeyError:
                pass

    @overrides(Index.items)
    def items(
        self,
        min = undefined,
        max = undefined,
        exclude_min = False,
        exclude_max = False,
        descending = False
    ):
        if descending:
            return self.__descending_items.keys(
                min = None if max is undefined
                      else DescEntry(
                          max,
                          lower_bound if exclude_max else upper_bound
                      ),
                max = None if min is undefined
                      else DescEntry(
                          min,
                          upper_bound if exclude_min else lower_bound
                      )
            )
        else:
            return self.__items.keys(
                min = None if min is undefined
                      else Entry(
                          min,
                          upper_bound if exclude_min else lower_bound
                      ),
                max = None if max is undefined
                      else Entry(
                          max,
                          lower_bound if exclude_max else upper_bound
                      )
            )

    @overrides(Index.min_key)
    def min_key(self, exclude_none = False):
        if exclude_none:
            for key in self.keys(min = None, include_min = False):
                return key
        else:
            return self.__items.minKey().key

    @overrides(Index.max_key)
    def max_key(self):
        return self.__items.maxKey().key

    @overrides(Index.__len__)
    def __len__(self):
        return len(self.__items)

    @overrides(Index.__bool__)
    def __bool__(self):
        return bool(self.__items)

    @overrides(Index.__contains__)
    def __contains__(self, key):
        for value in self.values(key = key):
            return True

        return False


class Entry(NamedTuple):

    key: Any
    value: Any = undefined

    def __eq__(self, other):
        return (
            not _cmp_key(self[0], other[0])
            and not _cmp_value(self[1], other[1])
        )

    def __gt__(self, other):

        key_comp = _cmp_key(self[0], other[0])

        if key_comp < 0:
            return False
        elif key_comp > 0:
            return True

        return _cmp_value(self[1], other[1]) > 0

    def __ge__(self, other):

        key_comp = _cmp_key(self[0], other[0])

        if key_comp < 0:
            return False
        elif key_comp > 0:
            return True

        return _cmp_value(self[1], other[1]) >= 0

    def __lt__(self, other):

        key_comp = _cmp_key(self[0], other[0])

        if key_comp > 0:
            return False
        elif key_comp < 0:
            return True

        return _cmp_value(self[1], other[1]) < 0

    def __le__(self, other):

        key_comp = _cmp_key(self[0], other[0])

        if key_comp > 0:
            return False
        elif key_comp < 0:
            return True

        return _cmp_value(self[1], other[1]) <= 0


class DescEntry(Entry):

    def __gt__(self, other):
        return Entry.__gt__(other, self)

    def __ge__(self, other):
        return Entry.__ge__(other, self)

    def __lt__(self, other):
        return Entry.__lt__(other, self)

    def __le__(self, other):
        return Entry.__le__(other, self)


def _cmp_key(a, b):

    if a == b:
        return 0

    if a is None:
        return -1

    if b is None:
        return 1

    if isinstance(a, tuple):
        for v1, v2 in zip(a, b):
            comp = _cmp_key(v1, v2)
            if comp:
                return comp
        else:
            return 0

    return 1 if a > b else -1

def _cmp_value(a, b):

    if a == b:
        return 0

    if a is undefined:
        return 0

    if b is undefined:
        return 0

    if a is upper_bound:
        return 1

    if a is lower_bound:
        return -1

    if b is upper_bound:
        return -1

    if b is lower_bound:
        return 1

    return 1 if a > b else -1

