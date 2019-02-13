#-*- coding: utf-8 -*-
"""Defines the `SingleValueIndex` class.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from BTrees.OOBTree import OOBTree
from cocktail.modeling import overrides
from .index import Index, undefined, Descending


class SingleValueIndex(Index):
    """An `index <Index>` where each key may only point to a single value."""

    accepts_multiple_values = False

    @overrides(Index.__init__)
    def __init__(self, pairs = None):
        self.__items = OOBTree()
        self.__descending_items = OOBTree()
        Index.__init__(self, pairs)

    @overrides(Index.add)
    def add(self, key, value):

        if key is None:
            raise ValueError("Can't use None as a key for a SingleValueIndex")

        self.__items[key] = value
        self.__descending_items[Descending(key)] = value

    @overrides(Index.remove)
    def remove(self, key, value = undefined):

        if value is not undefined \
        and self.get(key, undefined) != value:
            return

        if value is undefined:
            try:
                del self.__items[key]
                del self.__descending_items[key]
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
        min = self.__boundary(min, descending)
        max = self.__boundary(max, descending)

        if descending:
            min, max = max, min
            exclude_min, exclude_max = exclude_max, exclude_min

            for desc_key, value in self.__descending_items.iteritems(
                min = min,
                max = max,
                excludemin = exclude_min,
                excludemax = exclude_max
            ):
                yield (desc_key.value, value)
        else:
            for pair in self.__items.iteritems(
                min = min,
                max = max,
                excludemin = exclude_min,
                excludemax = exclude_max
            ):
                yield pair

    def __boundary(self, boundary, descending):
        if boundary is undefined:
            return None
        return Descending(boundary) if descending else boundary

    @overrides(Index.min_key)
    def min_key(self, exclude_none = False):
        if exclude_none:
            for key in list(self.keys()):
                if key is not None:
                    return key
        else:
            return self.__items.minKey()

    @overrides(Index.max_key)
    def max_key(self):
        return self.__descending_items.minKey().value

    @overrides(Index.__len__)
    def __len__(self):
        return len(self.__items)

    @overrides(Index.__bool__)
    def __bool__(self):
        return bool(self.__items)

    @overrides(Index.__contains__)
    def __contains__(self, key):
        return key in self.__items

    def __getitem__(self, key):
        """Get the value for the specified key.

        :param key: The key to retrieve the value for.

        :return: The value for the specified key.

        :raise KeyError: Raised if the indicated key isn't present in the
            index.
        """
        if isinstance(key, slice):
            raise ValueError(
                "Slicing an index is not supported; use keys()/values() "
                "instead")
        else:
            return self.__items[key]

    def get(self, key, default = None):
        """Get the value for the specified key, returning `default` if the key
        is undefined.

        :param key: The key to retrieve the value for.
        :param default: The value that should be returned if the key is not
            defined by the index.

        :return: The value for the specified key.
        """
        return self.__items.get(key, default)

