#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from persistent import Persistent
from BTrees.OOBTree import OOTreeSet

infinite = object()


class Index(Persistent):
    """A persistent index that supports multiple entries per key. Used to
    maintain an index for a non unique field.
    """

    def __init__(self):
        self.__items = OOTreeSet()

    def add(self, key, value):
        self.__items.insert((key, value))

    def remove(self, key, value):
        self.__items.remove((key, value))

    def discard(self, key, value):
        try:
            self.__items.remove((key, value))
        except KeyError:
            return False

        return True

    def __getitem__(self, key):

        if isinstance(key, slice):
            raise ValueError(
                "Slicing an index is not supported; use keys()/values() "
                "instead")
        else:
            return set(self.itervalues(min = key, max = key))

    def __delitem__(self, key):
        for pair in self[key]:
            del self.__items[pair]

    def keys(self,
        min = infinite,
        max = infinite,
        excludemin = False,
        excludemax = False):

        return list(self.iterkeys(
            min = min,
            max = max,
            excludemin = excludemin,
            excludemax = excludemax
        ))

    def values(self,
        min = infinite,
        max = infinite,
        excludemin = False,
        excludemax = False):

        return list(self.itervalues(
            min = min,
            max = max,
            excludemin = excludemin,
            excludemax = excludemax
        ))

    def items(self,
        min = infinite,
        max = infinite,
        excludemin = False,
        excludemax = False):

        return list(self.iteritems(
            min = min,
            max = max,
            excludemin = excludemin,
            excludemax = excludemax
        ))

    def itervalues(self,
        min = infinite,
        max = infinite,
        excludemin = False,
        excludemax = False):

        for pair in self.__items.keys(
            min = pair_comparator(min, excludemin, 1),
            max = pair_comparator(max, excludemax, -1)
        ):
            yield pair[1]

    def iterkeys(self,
        min = infinite,
        max = infinite,
        excludemin = False,
        excludemax = False):

        for pair in self.__items.keys(
            min = pair_comparator(min, excludemin, 1),
            max = pair_comparator(max, excludemax, -1)
        ):
            yield pair[0]

    def iteritems(self,
        min = infinite,
        max = infinite,
        excludemin = False,
        excludemax = False):

        for pair in self.__items.keys(
            min = pair_comparator(min, excludemin, 1),
            max = pair_comparator(max, excludemax, -1)
        ):
            yield pair

    def min_key(self):
        return self.__items.minKey()[0]

    def max_key(self):
        return self.__items.maxKey()[0]

    def __len__(self):
        return len(self.__items)

    def __notzero__(self):
        return bool(self.__items)

    def __iter__(self):
        return self.iterkeys()

    def __contains__(self, key):
        for pair in self.iterkeys(min = key, max = key):
            return True

        return False

    def has_key(self, key):
        return self.__contains__(key)


class PairComparator(object):

    def __init__(self, boundary, tie = 0):
        self.boundary = boundary
        self.tie = tie

    def __cmp__(self, pair):
        return cmp(self.boundary, pair[0]) or self.tie


def pair_comparator(boundary, excluded, tie):
    if boundary is infinite:
        return None
    return PairComparator(boundary, tie if excluded else -tie)

